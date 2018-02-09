# This file is used to create or update a single calendar for a given prof id or selst id
# Used for testing/troubleshooting only

from database_interaction import update_file, check_existence, add_to_db
from calendar_creation import create_calendar
import sys

params = sys.argv
prof = params[1]
selst = params[2]
update = params[3]

if len(params) != 4 or not prof.isdecimal() or not selst.isdecimal or update not in ['update', 'new']:
    print('''
    Usage: single_calendar_create_update.py [PROF] [SELST] [UPDATE]
    Create or update a single calendar for a given id
    PROF specifies the status of the id, 'prof' for professor and 'student' for student
    SELST specifies the id of the person
    UPDATE specifies whether the person should be added as a 'new' or receive an 'update' for their calendar
    ''')
    quit(1)


# Set the new prof and update statuses to True or False
prof = prof == 'prof'
update = update == 'update'

try:
    if update:
        update_file(selst, create_calendar(selst, prof=prof), prof=prof)
    elif check_existence(selst, prof=prof):
        print('Student or prof already exists, if you want to update - run as update')
    else:
        add_to_db(selst, create_calendar(selst, prof=prof), prof=prof)

except Exception as exc:
    print(exc)
    quit(1)
