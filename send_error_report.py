import sendgrid
import os
from sendgrid.helpers.mail import *


def send_email(errors):

    api_key = os.environ['SENDGRID_API_KEY']
    sg = sendgrid.SendGridAPIClient(apikey=api_key)
    from_email = Email("admin@timetable-cacs.herokuapp.com")
    to_email = Email("timetable.cacs@gmail.com")
    subject = "Error Report"
    content = Content("text/plain", "%d errors occurred when updating. Check them out!" % errors)
    message = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=message.get())
    if response.status_code != 202:
        raise ConnectionError('Cannot send email')


if __name__ == '__main__':
    send_email(12345)
