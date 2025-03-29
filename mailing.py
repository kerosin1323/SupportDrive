import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from platform import python_version


def send_simple_email(receiver_email, body):
    server = "smtp.yandex.ru"
    user = "kerosin1323@yandex.ru"
    password = "zfucdufhtralhtxh"

    recipients = [receiver_email]
    sender = "kerosin1323@yandex.ru"
    text = body
    html = '<html><head></head><body><p>' + text + '</p></body></html>'


    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Код проверки"
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg['Reply-To'] = sender
    msg['Return-Path'] = sender
    msg['X-Mailer'] = 'Python/' + (python_version())

    part_html = MIMEText(html, 'html')

    msg.attach(part_html)

    mail = smtplib.SMTP_SSL(server)
    mail.login(user, password)
    mail.sendmail(sender, recipients, msg.as_string())
    mail.quit()
