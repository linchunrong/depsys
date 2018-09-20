#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, smtplib, os
from email.message import EmailMessage
from depsys.sysconfig import SystemConfig


def email(receiver, attachment=None, content='FYI', subtype='plain'):
    """Send email"""
    conf = SystemConfig().get()
    mail_host = conf.smtp_server
    # auth_user = conf.smtp_user
    # auth_pass = conf.smtp_pwd
    sender = conf.smtp_user
    tolist = receiver

    message = EmailMessage()
    message['From'] = sender
    message['To'] = tolist
    subject = '最近发布记录 GENERATED AT ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    message['Subject'] = subject
    message.set_content(content, subtype=subtype)

    if attachment:
        message.add_attachment(open(attachment, 'r').read(), subtype='plane', filename=os.path.basename(attachment))

    try:
        s = smtplib.SMTP(mail_host, 25)
        # s.set_debuglevel(1)
        # s.ehlo()
        # s.starttls()
        # s.login(auth_user, auth_pass)
        s.send_message(message, sender, tolist)
        s.quit()
    except smtplib.SMTPException as e:
        return "Error: " + str(e)
    else:
        return "Send success!"
