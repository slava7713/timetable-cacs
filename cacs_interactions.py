import requests
import bs4
import arrow


def search(search_term):
    # Searches a student by name and gets a table of results

    search_page_text = requests.post('http://cacs.econ.msu.ru/index.php', params={'mnu': '75'}, data=search_term).text
    search_page_soup = bs4.BeautifulSoup(search_page_text, 'html5lib')
    table = search_page_soup.find('form', {'name': 'FrmStdSrch'}).next_sibling.next_sibling.next_sibling

    table['class'].append(' table-striped')
    del table['bgcolor']
    table.tbody.contents[2].append(search_page_soup.new_tag('td'))

    for row in table.tbody.contents[3:]:
        selst = int(row['onclick'].split('=')[2].strip()[:-1])
        del row['onclick']
        del row['bgcolor']

        new_column = search_page_soup.new_tag('td')

        new_form = search_page_soup.new_tag("form")
        new_form.attrs = {'class': 'form', 'method': 'POST'}

        new_form_button = search_page_soup.new_tag('button')
        new_form_button.attrs = {'type': 'submit', 'class': 'btn btn-primary', 'name': 'add',
                                 'value': selst}
        new_form_button.string = 'Выбрать'

        new_form.append(new_form_button)
        new_column.append(new_form)
        row.contents.append(new_column)
    return table


def request_page(selst, next_month=False):
    # Request the page of student with id selst for this or next month
    address = 'http://cacs.econ.msu.ru/index.php'

    # Have to do this since won't get next month otherwise
    session = requests.session()
    params = {'mnu': '75', 'selst': selst}

    if next_month:

        # Extra step since you always have to get current month first
        session.get(address, params=params)
        date = arrow.now().replace(months=+1).format('M.YYYY')
        params.update({'pMns': date})

    return session.get(address, params=params, timeout=15).text
