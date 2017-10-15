from flask import Flask, request, render_template, send_file
from cacs_interactions import search
from calendar_creation import create_calendar
from database_interaction import add_student, check_existence, serve_file
import os

# TODO: flask limiter
# TODO: figure out a way to find old selst and remove
# TODO: add errors, logging

app = Flask(__name__)


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

    response = serve_file(selst)
    if response:
        return response, 200, {'Content-Type': 'text/calendar; charset=utf-8'}
    else:
        return 'Error', 404


# # TODO: remove
# @app.route('/test')
# def test():
#     b = open("D:\\Users\\slava_000\\Desktop\\test.ics", 'rb')
#     return send_file(b, attachment_filename='123.ics',
#                      mimetype='text/calendar'), 200, {'Content-Type': 'text/calendar; charset=utf-8'}


@app.errorhandler(404)
def page_not_found(e):
    return e, 404


if __name__ == '__main__':
    try:
        debug = os.environ['FLASK_DEBUG']
    except KeyError:
        debug = False
    app.run(debug=debug)
