from database_interaction import purge_old, get_all_db, list_data
from send_error_report import send_email
from update_helper import update_individual_prof, update_individual_student
import logging
import os
import redis
from rq import Worker, Queue, Connection
log = logging.getLogger('gunicorn.error')

# Firstly, remove old subscriptions
purge_old()

# Get all items for update
items = get_all_db()


redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

# Start the queue
q = Queue(connection=conn)
for item in items[0]:
    q.enqueue(update_individual_student, item)
for item in items[1]:
    q.enqueue(update_individual_prof, item)

# Start the worker
listen = ['high', 'default', 'low']
with Connection(conn):
    worker = Worker(map(Queue, listen))
    worker.work()


# End by counting total student errors and if the number is high enough trigger a warning

total_errors, data = list_data(False)
if total_errors[1] > 5:
    log.critical('No updates for %d people!' % total_errors[1])
    send_email(total_errors[1])
