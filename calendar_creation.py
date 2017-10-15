import ics
import arrow
import bs4
from datetime import timedelta
from cacs_interactions import request_page


def month_parse(text):
    # Parse the html to separate it into days and classes

    html = bs4.BeautifulSoup(text, 'html5lib')
    month = html.find('table',
                      attrs={'style': "margin-top: 4", 'class': "TEXT1", 'cellspacing': "1", 'cellpadding': "0",
                             'bgcolor': "#8F928F", 'align': "center", 'border': "0", 'width': "100%"}).tbody
    month_parsed = []
    for days_of_the_week in month.find_all('tr', recursive=False):
        days = days_of_the_week.find_all('td', recursive=False)
        # Workaround to not break anything yet yield correct # of classes

        class_order = [int(x.text) for x in days[1].table.tbody.find_all('td')[1::2]]
        if class_order:
            # If month is not empty, proceed

            day_start = class_order[0]
            day_length = len(class_order)

            for day in days[1:]:
                items = day.table.tbody.find_all('tr', recursive=False)
                date = items[0].text
                temp = [''] * (day_length + 1)
                temp[0] = date
                if not date.strip():
                    continue
                for index, item in enumerate(items):
                    try:
                        data = item.find_all('div')[1]
                        if data.text.strip() == '':
                            continue
                    except IndexError:
                        continue
                    short_name_tag = data.b
                    room_tag = short_name_tag.find_next().find_next()
                    type_tag_text, prof_tag_text = data.text.split('[')[1].split(']')
                    location = '%s[%s]' % (room_tag.text, type_tag_text)
                    temp[index] = [short_name_tag.text, location, prof_tag_text]
                if day_start != 0:
                    for i in range(day_start - 1):
                        temp.insert(1, '')
                month_parsed.append(temp)

    return month_parsed


def get_days(selst):
    # Get the two months (or one if next is summer) for the selst
    days = []
    days += month_parse(request_page(selst))

    if not arrow.now().month == 6:
        days += month_parse(request_page(selst, next_month=True))

    return days


def create_file(days):
    # Create the .ics file from the parsed month

    calendar = ics.Calendar(imports='BEGIN:VCALENDAR\nPRODID:ics.py - http://git.io/lLljaA'
                                    '\nVERSION:1\nX-WR-CALDESC:Расписание\nEND:VCALENDAR')

    for day in days:
        for index, item in enumerate(day[1:]):
            if item != ['', ''] and item != '':
                event = ics.Event()
                event.begin = arrow.get(day[0], 'DD.MM.YYYY').replace(hours=6, minutes=+ (index * 100)).datetime
                event.duration = timedelta(hours=1, minutes=30)
                event.location = item[1]
                event.name = item[0]
                event.description = item[2]
                calendar.events.append(event)

    return bytes(str(calendar), 'utf-8')


def create_calendar(selst):
    # Go through the whole process: get the two months, parse them, create and return the file
    return create_file(get_days(selst))