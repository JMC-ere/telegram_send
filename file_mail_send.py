# -*-coding:utf-8-*-
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


def mail_send():
    email_user = '3softplus_bot@3softplus.com'
    email_password = '3softplus1234'

    recipients = ['wjdals9058@3softplus.com']

    # 참조
    # cc = ['']
    msg = MIMEMultipart()
    msg['Subject'] = '상용 통계파일'
    msg.attach(MIMEText('상용 통계데이터 파일', 'plain'))

    # 파일위치
    path = r'/file_mail_send.py'
    part = MIMEBase("application", "octet-stream")
    part.set_payload(open(path, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment;filename="%s"' % os.path.basename(path))
    msg.attach(part)

    # server = smtplib.SMTP_SSL(host='smtp.mailplug.co.kr',port=465)
    server = smtplib.SMTP_SSL(host='211.252.87.126', port=465)
    server.login(email_user, email_password)
    server.sendmail(email_user, recipients, msg.as_string())
    server.quit()

mail_send()
