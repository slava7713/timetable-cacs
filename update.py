from database_interaction import purge_old, get_all_db, update_file
from calendar_creation import create_calendar
from requests.exceptions import ReadTimeout
import logging
# Firstly, remove old subscriptions
purge_old()

# Then create the files for every selst
items = get_all_db()

for selst in items[0]:
    try:
        update_file(selst, create_calendar(selst, prof=False), prof=False)
    except ReadTimeout:
        logging.error('failed update for student %d' % selst)
        pass

for prr in items[1]:
    try:
        update_file(prr, create_calendar(prr, prof=True), prof=True)
    except ReadTimeout:
        logging.error('failed update for prof %d' % prr)
        pass
