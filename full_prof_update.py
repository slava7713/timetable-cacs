# This file is used to update all profs separately
# Used for testing/troubleshooting only


from database_interaction import purge_old, get_all_db, update_file
from calendar_creation import create_calendar
from requests.exceptions import ReadTimeout
import logging
log = logging.getLogger(__name__)

# Firstly, remove old subscriptions
purge_old()

# Then create the files for every selst
items = get_all_db()


for prr in items[1]:
    try:
        update_file(prr, create_calendar(prr, prof=True), prof=True)
    except ReadTimeout:
        log.error('failed update for prof %d' % prr)
        pass
