import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def send_email(errors):
    # create message object instance
    msg = MIMEMultipart()

    message = 'There were %d updating errors, check them out!' % errors

    # setup the parameters of the message
    password = os.environ['MAIL_PASSWORD']
    user = 'timetable.cacs@gmail.com'

    msg['From'] = user
    msg['To'] = user
    msg['Subject'] = 'Timetable Error Report'

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    # create server
    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()


if __name__ == '__main__':
    send_email(12345)
