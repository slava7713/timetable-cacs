from database_interaction import purge_old, get_all_db, update_file, list_data
from calendar_creation import create_calendar


# Firstly, remove old subscriptions
purge_old()

# Then create the files for every selst
items = get_all_db()

for selst in items[0]:
    try:
        update_file(selst, create_calendar(selst, prof=False), prof=False)
    except Exception as exc:
        log.error('failed update for student %d' % selst)
        log.error(exc)
        pass

for prr in items[1]:
    try:
        update_file(prr, create_calendar(prr, prof=True), prof=True)
    except Exception as exc:
        log.error('failed update for prof %d' % prr)
        log.error(exc)
        pass

# End by counting total student errors and if the number is high enough trigger a warning

total_errors, data = list_data(False)
if total_errors[1] > 5:
    log.critical('No updates for %d people!' % total_errors[1])
