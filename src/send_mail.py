# -*-coding:utf-8-*-
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


def mail_send(title, content):

    email_user = '3softplus_bot@3softplus.com'
    email_password = '3softplus1234'

    # 받는사람
    recipients = ['wjdals9058@3softplus.com', 'object@3softplus.com']

    # 참조
    # cc = ['']
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = ", ".join(recipients)
    msg['Bcc'] = "3softplus_bot@3softplus.com"
    # msg['Cc'] = ", ".join(cc)
    msg['Subject'] = title

    body = MIMEText(content, 'html')
    msg.attach(body)

    text = msg.as_string()

    # server = smtplib.SMTP_SSL(host='smtp.mailplug.co.kr',port=465)
    server = smtplib.SMTP_SSL(host='211.252.87.126', port=465)
    server.login(email_user, email_password)
    server.sendmail(email_user, recipients, text)
    server.quit()
