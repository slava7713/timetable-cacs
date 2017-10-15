from database_interaction import purge_old, get_all_selst, update_file
from calendar_creation import create_calendar

# Firstly, remove old subscriptions
purge_old()

# Then create the files for every selst
for selst in get_all_selst():
    update_file(selst, create_calendar(selst))
