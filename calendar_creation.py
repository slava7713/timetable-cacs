import ics
import arrow
import bs4
from datetime import timedelta
from cacs_interactions import request_page
import logging
log = logging.getLogger(__name__)


def get_lesson_start_time(number):
    return [0, 100, 200, 300, 400, 500, 595, 690, 785, 880, 975][number - 1]


class Lesson:

    """

    A single lesson with all the appropriate data
        number - 1 to 8
        date - date in DD.MM.YYYY format

    """

    def __init__(self, number, date, short_name, long_name, location, prof, notes=""):
        self.datetime = arrow.get(date, 'DD.MM.YYYY').replace(hour=6).\
            shift(minutes=get_lesson_start_time(number)).datetime
        self.short_name = short_name
        self.long_name = long_name
        self.location = location
        self.prof = prof
        self.notes = notes

    def __str__(self):
        return "%s. %s" % (str(self.datetime), self.short_name)

    __iter__ = __str__


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
                if not date.strip():
                    continue
                for index, item in enumerate(items):
                    try:
                        all_lessons_at_that_time = item.find_all('div', {'id': 'LESS'})

                        if all_lessons_at_that_time[0].text.strip() == '':
                            continue
                    except IndexError:
                        continue
                    for data in all_lessons_at_that_time:
                        short_name_tag = data.b
                        room_tag = short_name_tag.find_next().find_next()
                        type_tag_text, prof_tag_text = data.text.split('[')[1].split(']')
                        location = '%s[%s]' % (room_tag.text, type_tag_text)
                        temp = Lesson(index + day_start - 1, date, short_name_tag.text, data['title'], location,
                                      prof_tag_text, "")
                        month_parsed.append(temp)

    return month_parsed


def get_days(n, prof):
    # Get the two months (or one if next is summer) for the selst
    days = []

    try:
        days += month_parse(request_page(n, prof))

    except Exception as exc:
        log.error('Error with parsing month for %s' % str(n))
        raise exc

    if not arrow.now().month == 6:
        try:
            days += month_parse(request_page(n, prof, next_month=True))

        except Exception as exc:
            log.error('Error with parsing next month for %s' % str(n))
            raise exc

    return days


def create_file(lessons):
    # Create the .ics file from the parsed month

    calendar = ics.Calendar(imports='BEGIN:VCALENDAR\nPRODID:ics.py - http://git.io/lLljaA'
                                    '\nVERSION:1\nX-WR-CALDESC:Расписание\nEND:VCALENDAR')

    for lesson in lessons:
        event = ics.Event()
        event.begin = lesson.datetime
        event.duration = timedelta(hours=1, minutes=30)
        event.location = lesson.location
        event.name = lesson.short_name
        event.description = '%s - %s' % (lesson.prof, lesson.long_name)
        calendar.events.add(event)

    return bytes(str(calendar), 'utf-8')


def create_calendar(n, prof):
    # Go through the whole process: get the two months, parse them, create and return the file
    return create_file(get_days(n, prof))
