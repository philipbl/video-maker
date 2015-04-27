#!/usr/bin/env python

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to, subject, message, html=False):
    gmail_user = "philiplundrigan@gmail.com"
    gmail_pwd = "tamtepzumnexnknx"

    msg = MIMEMultipart('alternative')
    msg['To'] = to
    msg['From'] = gmail_user
    msg['Subject'] = subject

    if html:
        body = """\
<html>
    <head></head>
    <body>
        {}
    </body>
</html>
""".format(message)

        msg.attach(MIMEText(body, 'html'))

    else:
        msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(gmail_user, to, msg.as_string())
        server.close()
    except:
        print "Failed to send mail..."


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Send emails through Gmail.')
    parser.add_argument('-t', '--to', type=str, required=True,
                        help='Who the email should be sent to.')
    parser.add_argument('-s', '--subject', type=str, required=True,
                        help='The subject of the email.')
    parser.add_argument('-m', '--message', type=str, required=True,
                        help='The body of the email.')
    parser.add_argument('--html', action='store_true',
                        help='Send message as a HTML email.')

    args = parser.parse_args()

    send_email(args.to, args.subject, args.message, args.html)
