#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, json, smtplib, os, setting
from email.message import EmailMessage
from depsys.sysconfig import SystemConfig


def email(receiver, attachment=None, subject=None, content='FYI', subtype='plain'):
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


def wechat(message):
    """Send WeChat"""
    # args in need, API doc refer to - https://work.weixin.qq.com/api/doc
    corpid = setting.corpid
    corpsecret = setting.corpsecret

    ### get access_token ####
    get_token_url = setting.API_URL + "gettoken?corpid=" + corpid + "&corpsecret=" + corpsecret
    request = urllib.request.Request(get_token_url)
    try:
        response = urllib.request.urlopen(request)
    except Exception as Err:
        return "Error: " + str(Err)
    else:
        page = response.read()

    access_token = json.loads(page)['access_token']
    ##########################
    ### send message #########
    send_url = setting.API_URL + "message/send?access_token=" + access_token
    send_text = {
        "touser": "@all",
        "toparty": "@all",
        "msgtype": "text",
        "agentid": setting.AgentId,
        "text": {
            "content": message
        },
        "safe": 0
    }

    send_text = bytes(json.dumps(send_text, ensure_ascii=False), encoding='utf-8')
    request = urllib.request.Request(send_url, data=send_text)
    try:
        response = urllib.request.urlopen(request)
    except Exception as Err:
        return "Error: " + str(Err)
    else:
        # status = json.loads(response.read())
        return "Send success!"
