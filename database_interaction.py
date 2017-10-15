from urllib import parse
import psycopg2
from datetime import datetime, timedelta
import os

# Database schema: (selst integer, last_access date, last_update date, file bytea)

parse.uses_netloc.append('postgres')

try:
    url = parse.urlparse(os.environ['DATABASE_URL'])
except KeyError:
    url = parse.urlparse('postgres://user:123@localhost:5432/timetable')

# Setup the connection to the database
conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port,
)
conn.autocommit = True
cur = conn.cursor()

# A little shortcut
today = datetime.now().date


def check_existence(selst):
    # Checks whether selst is in db so as not to create the file a second time

    cur.execute('SELECT * FROM econ WHERE selst = %s', (selst,))
    if cur.fetchone():
        return True


def add_student(selst, file):
    # Add a new selst and file

    last_access = today()
    last_update = last_access

    cur.execute('INSERT INTO econ (selst, last_access, last_update, file) VALUES (%s, %s, %s, %s)',
                (selst, last_access, last_update, file))


def update_file(selst, file):
    # Update the file of specified selst

    cur.execute('UPDATE econ SET last_update = %s, file = %s WHERE selst = %s', (today(), file, selst))


def serve_file(selst):
    # Fetch selst's file and update last_access

    cur.execute('SELECT file FROM econ WHERE selst = %s', (selst,))
    result = cur.fetchone()

    if result:
        cur.execute('UPDATE econ SET last_access = %s WHERE selst = %s', (today(), selst))
        return bytes(result[0])


def remove_student(selst):
    # Remove student

    cur.execute('DELETE FROM econ WHERE selst = %s', (selst,))


def get_all_selst():
    # Get a list of all selst

    cur.execute('SELECT selst FROM econ')
    result = cur.fetchall()
    return [item[0] for item in result]


def list_data():
    # List all data for statistics page ((selst, last_access, last_update), (error_no_access, error_no_update))
    # Errors = (no access for 90 days, no update for 3 days)

    cur.execute('SELECT selst, last_access, last_update FROM econ')
    result = cur.fetchall()

    new_result = []
    no_access_total = 0
    no_update_total = 0

    for item in result:
        error_no_access = False
        error_no_update = False

        if today() - item[1] > timedelta(days=90):
            error_no_access = True
            no_access_total += 1

        if today() - item[2] > timedelta(days=3):
            error_no_update = True
            no_update_total += 1

        new_result.append((item, (error_no_access, error_no_update)))

    totals = (no_access_total, no_update_total)

    return totals, new_result


def purge_old():
    # Remove all selst with last_access of more than 180 days ago

    cur.execute('SELECT selst, last_access FROM econ')
    result = cur.fetchall()
    for item in result:
        if today() - item[1] > timedelta(days=180):
            remove_student(item[0])
