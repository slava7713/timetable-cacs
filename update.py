from database_interaction import purge_old, get_all_db, update_file, list_data
from calendar_creation import create_calendar
from send_error_report import send_email
from rq import Queue
from worker import conn
import logging
log = logging.getLogger('gunicorn.error')


def update_individual_student(selst):
    try:
        update_file(selst, create_calendar(selst, prof=False), prof=False)
    except Exception as exc:
        log.error('failed update for student %d' % selst)
        log.error(exc)
        pass


def update_individual_prof(prr):
    try:
        update_file(prr, create_calendar(prr, prof=True), prof=True)
    except Exception as exc:
        log.error('failed update for prof %d' % prr)
        log.error(exc)
        pass

# Firstly, remove old subscriptions
purge_old()

# Get all items for update
items = get_all_db()

# Start the queue
q = Queue(connection=conn)
for item in items[0]:
    q.enqueue(update_individual_student, item)
for item in items[1]:
    q.enqueue(update_individual_prof, item)

# End by counting total student errors and if the number is high enough trigger a warning

total_errors, data = list_data(False)
if total_errors[1] > 5:
    log.critical('No updates for %d people!' % total_errors[1])
    send_email(total_errors[1])
