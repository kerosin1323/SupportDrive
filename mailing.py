import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes
from platform import python_version


def send_simple_email(receiver_email, body, username):
    server = "smtp.yandex.ru"
    user = "kerosin1323@yandex.ru"
    password = "zfucdufhtralhtxh"

    recipients = [receiver_email]
    sender = "kerosin1323@yandex.ru"

    msg = EmailMessage()
    msg['Subject'] = "Код проверки"
    msg['From'] = f'SupportDrive <{sender}>'
    msg['To'] = ', '.join(recipients)
    msg['Reply-To'] = sender
    msg['Return-Path'] = sender
    msg['X-Mailer'] = 'Python/' + (python_version())
    msg.set_content('Пароль')
    image_cid = make_msgid(domain='xyz.com')
    msg.add_alternative("""\
    <html>
        <head>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <div style="width:100%; background-color:#293245;margin:auto;color:white ">
                <div style="display:flex;padding-top:20px;color:white;margin-left:20px">
                    <img src="cid:{image_cid}" height="40px" width="40px">
                    <div style="font-size:20px;padding-top:5px">
                        SupportDrive
                    </div>
                </div>  
                <div style="word-wrap:break-word;margin:20px;padding-bottom:20px">
                    Спасибо, {username}, что зарегстрировали аккаунт на SupportDrive! Прежде чем мы начнем, нам нужно подтвердить, что это вы. Введите представленный ниже код в поле ввода для подтверждения почты: 
                </div>
                <div style="font-size:50px;position: absolute;top: 50%;text-align: center;bottom: 50%;left: 50%;transform: translate(-50%, -50%);">{password}</div>       
                <hr style='background-color:black'>
                <div style="font-size:15px;padding-bottom:10px;margin-left:10px">Нужна помощь? <a href='https://t.me/Sergey_Orlov12345'>Свяжитесь с коммандой поддержки</a></div> 
            </div>
    """.format(image_cid=image_cid[1:-1], username=username, password=body), subtype='html')
    with open('./static/logo/logo.png', 'rb') as img:
        maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
        msg.get_payload()[1].add_related(img.read(),maintype = maintype,subtype = subtype,cid = image_cid)


    mail = smtplib.SMTP_SSL(server)
    mail.login(user, password)
    mail.sendmail(sender, recipients, msg.as_string())
    mail.quit()