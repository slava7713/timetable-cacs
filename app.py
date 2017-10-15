from flask import Flask, request, render_template, Response
from cacs_interactions import search
from functools import wraps
from calendar_creation import create_calendar
from database_interaction import add_student, check_existence, serve_file, list_data
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

# TODO: add errors, logging

app = Flask(__name__)

username = os.environ['FLASK_LOGIN']
password = os.environ['FLASK_PASSWORD']

# Set up the limiter to prevent too many requests
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["50 per day", "20 per hour"]
)


def requires_auth(f):
    # To require login for stats page

    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not (auth.username == username and auth.password == password):
            return Response('Wrong password', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated


@app.route('/', methods=['GET', 'POST'])
def index():
    # Main page that provides search, selection and subscription

    search_results = ''
    file = ''

    try:
        request_search = request.form['search']
    except KeyError:
        request_search = ''

    try:
        request_add = request.form['add']
    except KeyError:
        request_add = ''

    if request.method == 'POST' and request_search:
        # If the search form was posted get the results and display them
        search_term = {'VZESH': request_search.encode('windows-1251')}
        search_results = search(search_term)

    if request.method == 'POST' and request_add:
        # If the name was selected, check if it exists, if not add it to the db, create the calendar and serve the link
        selst = request_add
        if not check_existence(selst):
            add_student(selst, create_calendar(selst))
        file = '%s.ics' % selst

    return render_template('main.html', search_results=search_results, file=file)


@app.route('/<selst>.ics')
def send_file(selst):
    # Serve the file from db

    if selst.isdecimal():
        response = serve_file(selst)
        if response:
            return response, 200, {'Content-Type': 'text/calendar; charset=utf-8'}
    return 'Error', 404


@app.route('/stats')
@requires_auth
def show_stats():
    # Show overall stats

    totals, items = list_data()
    return render_template('stats.html', totals=totals, items=items)


@app.errorhandler(404)
def page_not_found(e):
    return e, 404


if __name__ == '__main__':

    if os.environ['FLASK_DEBUG']:
        app.run(host='192.168.10.101', debug=True)
    else:
        app.run()
