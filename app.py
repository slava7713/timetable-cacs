from flask import Flask, request, render_template
import requests
import bs4

#TODO flask limiter
app = Flask(__name__)

# IP = "127.0.0.1"
# PORT = 8080
# DEBUG = False


@app.route('/', methods=['GET', 'POST'])
def index():
    search_results = ''
    add_id = ''
    if request.method == 'POST' and request.form['search']:
        search_term = {'VZESH': request.form['search'].encode('windows-1251')}
        search_page_text = requests.post('http://cacs.econ.msu.ru/index.php', params={'mnu': '75'}, data=search_term).text
        search_page_soup = bs4.BeautifulSoup(search_page_text, 'html5lib')
        table = search_page_soup.find('form', {'name': 'FrmStdSrch'}).next_sibling.next_sibling.next_sibling

        for row in table.tbody.contents[3:]:

            selst = int(row['onclick'].split('=')[2].strip()[:-1])
            del row['onclick']

            new_column = search_page_soup.new_tag('td')

            new_form = search_page_soup.new_tag("form")
            new_form.attrs = {'class': 'form', 'method': 'POST'}

            new_form_button = search_page_soup.new_tag('button')
            new_form_button.attrs = {'type': 'submit', 'class': 'btn btn-default', 'name': 'add',
                                    'value': selst}
            new_form_button.string = 'Выбрать'

            new_form.append(new_form_button)
            new_column.append(new_form)
            row.contents.append(new_column)

        search_results = table

    elif request.method == 'POST' and request.form['add']:
        pass

    return render_template('main.html', search_results=search_results, add_id=add_id)


@app.errorhandler(404)
def page_not_found(e):
    return e, 404


if __name__ == '__main__':
    app.run()
