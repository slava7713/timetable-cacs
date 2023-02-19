from urllib import parse
import psycopg2
from datetime import datetime, timedelta
import os

# Database schema: (selst integer, last_access date, last_update date, file bytea)

parse.uses_netloc.append('postgres')

url = parse.urlparse(os.environ['DATABASE_URL'])

# Set up the connection to the database
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


def check_existence(n, prof):
    # Checks whether selst is in db so as not to create the file a second time
    if prof:
        cur.execute('SELECT * FROM econ_prof WHERE prr = %s', (n,))
    else:
        cur.execute('SELECT * FROM econ WHERE selst = %s', (n,))
    if cur.fetchone():
        return True


def add_to_db(n, file, prof):
    # Add a new selst and file
    import time
    time.sleep(5)
    last_access = today()
    last_update = last_access
    if prof:
        cur.execute('INSERT INTO econ_prof (prr, last_access, last_update, file) VALUES (%s, %s, %s, %s)',
                    (n, last_access, last_update, file))
    else:
        cur.execute('INSERT INTO econ (selst, last_access, last_update, file) VALUES (%s, %s, %s, %s)',
                    (n, last_access, last_update, file))


def update_file(n, file, prof):
    # Update the file of specified selst
    if prof:
        cur.execute('UPDATE econ_prof SET last_update = %s, file = %s WHERE prr = %s', (today(), file, n))
    else:
        cur.execute('UPDATE econ SET last_update = %s, file = %s WHERE selst = %s', (today(), file, n))


def serve_file(n, prof):
    # Fetch file for selected id and update last_access

    if prof:
        cur.execute('SELECT file FROM econ_prof WHERE prr = %s', (n,))
        result = cur.fetchone()

        if result:
            cur.execute('UPDATE econ_prof SET last_access = %s WHERE prr = %s', (today(), n))
            return bytes(result[0])
    else:
        cur.execute('SELECT file FROM econ WHERE selst = %s', (n,))
        result = cur.fetchone()

        if result:
            cur.execute('UPDATE econ SET last_access = %s WHERE selst = %s', (today(), n))
            return bytes(result[0])


def remove_from_db(n, prof):
    # Remove student
    if prof:
        cur.execute('DELETE FROM econ_prof WHERE prr = %s', (n,))
    else:
        cur.execute('DELETE FROM econ WHERE selst = %s', (n,))


def get_all_db():
    # Get a list of all selst

    cur.execute('SELECT selst FROM econ')
    result = cur.fetchall()
    students = [item[0] for item in result]
    cur.execute('SELECT prr FROM econ_prof')
    result = cur.fetchall()
    profs = [item[0] for item in result]
    return [students, profs]


def list_data(prof):
    # List all data for statistics page ((selst/prr, last_access, last_update), (error_no_access, error_no_update))
    # Errors = (no access for 90 days, no update for 3 days)
    if prof:
        cur.execute('SELECT prr, last_access, last_update FROM econ_prof')
    else:
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
    # Remove all items with last_access of more than 180 days ago

    cur.execute('SELECT selst, last_access FROM econ')
    students = cur.fetchall()
    cur.execute('SELECT prr, last_access FROM econ_prof')
    profs = cur.fetchall()
    for item in students:
        if today() - item[1] > timedelta(days=180):
            remove_from_db(item[0], prof=False)
    for item in profs:
        if today() - item[1] > timedelta(days=180):
            remove_from_db(item[0], prof=True)
