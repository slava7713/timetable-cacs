from flask import Flask, request, render_template, Response, send_from_directory, redirect
from cacs_interactions import search_student, search_professor
from functools import wraps
from calendar_creation import create_calendar
from database_interaction import add_to_db, check_existence, serve_file, list_data
from flask_limiter import Limiter
import os
import logging

app = Flask(__name__, static_folder='static', static_url_path='')
app.logger.setLevel('ERROR')
logging.getLogger('werkzeug').setLevel('ERROR')
logging.getLogger('gunicorn.error').setLevel('ERROR')

app.debug = False

username = os.environ['FLASK_LOGIN']
password = os.environ['FLASK_PASSWORD']

# Set up the limiter to prevent too many requests
limiter = Limiter(
    app,
    default_limits=["1000 per day", "100 per hour"]
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
    # Main page that provides search_student, selection and subscription

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
        # If the search_student form was posted get the results and display them
        search_term = {'VZESH': request_search.encode('windows-1251')}
        search_results = search_student(search_term)

    if request.method == 'POST' and request_add:
        # If the name was selected, check if it exists, if not add it to the db, create the calendar and serve the link
        selst = request_add
        if not check_existence(selst, prof=False):
            add_to_db(selst, create_calendar(selst, prof=False), prof=False)
        file = '%s.ics' % selst

    return render_template('main.html', search_results=search_results, file=file)


@app.route('/prof', methods=['GET', 'POST'])
def prof():
    # Like main page but for professors

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
        search_term = {'VZTSH': request_search.encode('windows-1251')}
        search_results = search_professor(search_term)

    if request.method == 'POST' and request_add:
        # If the name was selected, check if it exists, if not add it to the db, create the calendar and serve the link
        prr = request_add
        if not check_existence(prr, prof=True):
            add_to_db(prr, create_calendar(prr, prof=True), prof=True)
        file = 'prof/%s.ics' % prr

    return render_template('prof.html', search_results=search_results, file=file)


@app.route('/<selst>.ics')
def send_student_file(selst):
    # Serve the file from db
    if selst.isdecimal():
        response = serve_file(selst, prof=False)
        if response:
            return response, 200, {'Content-Type': 'text/calendar; charset=utf-8'}
    return 'Error', 404


@app.route('/<selst>.ics/')
def redirect_student(selst):
    # Redirect the link to file
    return redirect('/%s.ics' % selst)


@app.route('/prof/<prr>.ics')
def send_prof_file(prr):
    # Serve the file from db

    if prr.isdecimal():
        response = serve_file(prr, prof=True)
        if response:
            return response, 200, {'Content-Type': 'text/calendar; charset=utf-8'}
    return 'Error', 404


@app.route('/<prof/<prr>.ics/')
def redirect_prof(prr):
    # Redirect the link to file
    return redirect('/prof/%s.ics' % prr)


@app.route('/stats')
@requires_auth
def show_stats():
    # Show overall stats

    totals, items = list_data(prof=False)
    return render_template('stats.html', totals=totals, items=items)


@app.route('/prof/stats')
@requires_auth
def show_prof_stats():
    # Show overall prof stats

    totals, items = list_data(prof=True)
    return render_template('stats.html', totals=totals, items=items)


@app.route('/robots.txt')
@app.route('/favicon.ico')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.errorhandler(404)
def page_not_found(e):
    return e, 404


if __name__ == '__main__':

    if os.environ['FLASK_DEBUG'] == 'DEBUG':
        logging.getLogger('werkzeug').setLevel(logging.NOTSET)
        app.logger.setLevel('DEBUG')
        app.run(host='127.0.0.1', debug=True)
    else:
        print('Should not run like that')
