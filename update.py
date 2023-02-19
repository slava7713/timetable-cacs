from database_interaction import purge_old, get_all_db, list_data
from update_helper import update_individual_prof, update_individual_student
import logging

log = logging.getLogger('gunicorn.error')

# Firstly, remove old subscriptions
purge_old()

# Get all items for update
items = get_all_db()


for item in items[1]:
    try:
        update_individual_prof(item)
    except Exception as exc:
        log.error("Error updating prof %s" % item)
        log.error(exc)

for item in items[0]:
    try:
        update_individual_student(item)
    except Exception as exc:
        log.error("Error updating student %s" % item)
        log.error(exc)

# End by counting total student errors and if the number is high enough trigger a warning

total_errors, data = list_data(False)
if total_errors[1] > 5:
    log.critical('No updates for %d people!' % total_errors[1])
