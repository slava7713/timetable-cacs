from database_interaction import update_file
from calendar_creation import create_calendar
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
