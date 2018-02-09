from database_interaction import purge_old, get_all_db, update_file
from calendar_creation import create_calendar
from requests.exceptions import ReadTimeout
import logging
# Firstly, remove old subscriptions
purge_old()

# Then create the files for every selst
items = [22964, 22982, 22801, 22778, 23110, 22757, 22582, 22703, 22785, 22913, 22907, 22889, 23144, 22891, 22807]

for selst in items:
    try:
        update_file(selst, create_calendar(selst, prof=False), prof=False)
    except ReadTimeout:
        logging.error('failed update for student %d' % selst)
        pass