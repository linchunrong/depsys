#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, smtplib, os, setting, requests
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
        return True


def wechat(type, message=None, post_file=None):
    """Send message via WeChat"""
    # args in need, API doc refer to - https://work.weixin.qq.com/api/doc
    corpid = setting.corpid
    corpsecret = setting.corpsecret

    access_token = get_token(corpid=corpid, corpsecret=corpsecret)
    send_url = setting.API_URL + "message/send?access_token=" + access_token
    send_data = {
        "touser": "@all",
        "toparty": "@all",
        "msgtype": type,
        "agentid": setting.AgentId,
        "safe": 0
    }
    if type == 'file':
        media_id = get_media_id(type, access_token, post_file)
        send_data[type] = {"media_id": media_id}
    if type == 'text':
        send_data[type] = {"content": message}

    send_data = bytes(json.dumps(send_data, ensure_ascii=False), encoding='utf-8')
    # send message
    try:
        request = requests.post(send_url, data=send_data)
    except Exception as Err:
        return "Error: " + str(Err)
    else:
        # page = request.json()
        return True


def get_token(corpid, corpsecret):
    """"Get wechat access_token"""
    get_token_url = setting.API_URL + "gettoken?corpid=" + corpid + "&corpsecret=" + corpsecret
    try:
        request = requests.get(get_token_url)
    except Exception as Err:
        return "Error: " + str(Err)
    else:
        page = request.json()

    access_token = page['access_token']

    return access_token


def get_media_id(type, access_token, target_file):
    """Get wechat media_id"""
    get_media_id_url = setting.API_URL + "media/upload?access_token=" +  access_token + "&type=" + type

    with open(target_file, 'rb') as f:
        files = {'file': f}
        try:
            request = requests.post(get_media_id_url, files=files)
        except Exception as Err:
            return "Error: " + str(Err)
        else:
            page = request.json()

    media_id = page['media_id']

    return media_id
