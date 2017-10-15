from urllib import parse
import psycopg2
from datetime import datetime
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
    pass


def get_all_selst():
    # Get a list of all selst

    cur.execute('SELECT selst FROM econ')
    result = cur.fetchall()
    return [item[0] for item in result]


def purge_old():
    # Find all old calendars and remove them
    pass


