import ics
import arrow
import bs4
from datetime import timedelta
from cacs_interactions import request_page


def month_parse(text):
    # TODO: description and rework this mess

    soup_find_all_result = bs4.BeautifulSoup(text, 'html5lib').find_all("table", attrs={'class': "TEXT1",
                                                                                        'width': "100%",
                                                                                        'height': "100%",
                                                                                        'cellspacing': "0",
                                                                                        'cellpadding': "0",
                                                                                        'border': "0",
                                                                                        'align': "center"})
    month_unparsed = []
    month_parsed = []
    day_length = []

    for r in soup_find_all_result:
        r = str(r).replace('<br/>', '\n')
        g = bs4.BeautifulSoup(r, 'html5lib')
        text_with_fixed_errors = g.text
        t = [x.replace('\xa0', '') for x in text_with_fixed_errors.split('  ')]
        day_element_placeholder = []
        for elem in t:
            day_element_placeholder.append(elem)
        month_unparsed.append(day_element_placeholder)

    if month_unparsed[0] == [''] or month_unparsed[0][0].replace('.', '').isnumeric():
        return []

    for j, k in enumerate(month_unparsed):
        if k[1][0].isnumeric():
            for m in range(1, len(k)):
                day_length.append(int(k[m][0]))
        break
    for day in month_unparsed:
        day_parsed = []

        if not day[0]:
            continue

        elif day[0].replace('.', '').isnumeric():
            day_parsed.append(day[0])

            for n in range(day_length[0] - 1):
                day.insert(1, '\n\n')

            for m in range(1, day_length[-1] + 1):
                if not day[m]:
                    day_parsed.append(['', ''])
                    continue
                if day[m][0].isnumeric():
                    day[m] = day[m][1:]
                if day[m]:
                    day[m] = [x for x in day[m].split('\n')[0:2]]
                day_parsed.append(day[m])
            month_parsed.append(day_parsed)
    return month_parsed


def create_calendar(selst):
    # TODO: add comments
    # TODO: get the new version from laptop!!

    calendar = ics.Calendar(imports='BEGIN:VCALENDAR\nPRODID:ics.py - http://git.io/lLljaA'
                                    '\nVERSION:1\nX-WR-CALDESC:Расписание\nEND:VCALENDAR')
    full = []
    full += month_parse(request_page(selst))

    if not arrow.now().month == 6:

        full += month_parse(request_page(selst, next_month=True))

    for day in full:
        for index, item in enumerate(day[1:]):
            if item != ['', ''] and item != '':
                event = ics.Event()
                event.begin = arrow.get(day[0], 'DD.MM.YYYY').replace(hours=6, minutes=+ (index * 100)).datetime
                event.duration = timedelta(hours=1, minutes=30)
                event.location = item[1]
                event.name = item[0]
                calendar.events.append(event)

    return bytes(str(calendar), 'utf-8')
