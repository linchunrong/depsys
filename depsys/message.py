#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
import smtplib
from email.message import EmailMessage
from depsys.sysconfig import SystemConfig


def email(receiver, attachment=None):
    """Send email"""
    conf = SystemConfig().get()
    mail_host = conf.smtp_server
    fromaddr = conf.smtp_user
    # frompass = conf.smtp_pwd
    sender = fromaddr
    tolist = receiver

    message = EmailMessage()
    message['From'] = sender
    message['To'] = tolist
    subject = 'Deploy info ' + time.strftime("%Y-%m-%d", time.localtime())
    message['subject'] = subject
    message.set_content("FYI")

    if attachment:
        message.add_attachment(open(attachment, 'r').read(), subtype='plane', filename=os.path.basename(attachment))

    try:
        s = smtplib.SMTP(mail_host, 25)
        # s.login(fromaddr, frompass)
        s.send_message(message, sender, tolist)
        s.quit()
        return "Send success!"

    except smtplib.SMTPException as e:
        return "Error: " + str(e)
