from database_interaction import purge_old, get_all_db, update_file
from calendar_creation import create_calendar

# Firstly, remove old subscriptions
purge_old()

# Then create the files for every selst
items = get_all_db()
for selst in items[0]:
    update_file(selst, create_calendar(selst, prof=False), prof=False)

for prr in items[1]:
    update_file(prr, create_calendar(prr, prof=True), prof=True)
