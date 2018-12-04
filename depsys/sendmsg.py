#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, smtplib, os, requests
from email.message import EmailMessage
from depsys.sysconfig import SystemConfig
from setting import *


def email(receiver, attachment=None, subject=None, content='FYI', subtype='plain'):
    """Send email"""
    conf = SystemConfig().get()
    mail_host = conf.smtp_server
    # auth_user = conf.smtp_user
    # auth_pass = conf.smtp_pwd
    sender = conf.mail_address
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


def wechat(msgtype, message=None, post_file=None):
    """Send message via WeChat"""
    # API doc refer to - https://work.weixin.qq.com/api/doc, get variables rom setting
    access_token = get_token(corpid=CORPID, corpsecret=CORPSECRET)
    # if there's error when call get_token, return Error
    if "Error" in access_token:
        return access_token

    send_url = API_URL + "message/send?access_token=" + access_token
    send_data = {
        "touser": "@all",
        "toparty": "@all",
        "msgtype": msgtype,
        "agentid": AGENTID,
        "safe": 0
    }
    if msgtype == 'file':
        media_id = get_media_id(msgtype, access_token, target_file=post_file)
        # if there's error when call get_media, return Error
        if "Error" in media_id:
            return media_id
        send_data[msgtype] = {"media_id": media_id}
    if msgtype == 'text':
        send_data[msgtype] = {"content": message}

    send_data = bytes(json.dumps(send_data, ensure_ascii=False), encoding='utf-8')
    # send message
    try:
        request = requests.post(send_url, data=send_data)
    except Exception as Err:
        return "Error: " + str(Err)
    else:
        page = request.json()
        # refer to get_token/get_media
        if page['errcode'] == 0:
            return True
        else:
            return "Error: " + str(page['errmsg'])


def get_token(corpid, corpsecret):
    """"Get wechat access_token"""
    get_token_url = API_URL + "gettoken?corpid=" + corpid + "&corpsecret=" + corpsecret
    try:
        request = requests.get(get_token_url)
    except Exception as Err:
        return "Error: " + str(Err)
    else:
        page = request.json()
        # example of page content
        # {'errcode': 40013, 'errmsg': 'invalid corpid', '*key':' *values'}
        # only when errcode is 0 means success
        if page['errcode'] == 0:
            access_token = page['access_token']
            return access_token
        else:
            return "Error: " + str(page['errmsg'])


def get_media_id(msgtype, access_token, target_file):
    """Get wechat media_id"""
    get_media_id_url = API_URL + "media/upload?access_token=" + access_token + "&type=" + msgtype

    with open(target_file, 'rb') as f:
        files = {'file': f}
        try:
            request = requests.post(get_media_id_url, files=files)
        except Exception as Err:
            return "Error: " + str(Err)
        else:
            page = request.json()
            # example of page content
            # {
            #   "errcode": 0,
            #   "errmsg": ""，
            #   "type": "image",
            #   "media_id": "1G6nrLmr5EC3MMb_-zK1dDdzmd0p7cNliYu9V5w7o8K0",
            #   "created_at": "1380000000"
            #  }
            # only when errcode is 0 means success
            if page['errcode'] == 0:
                media_id = page['media_id']
                return media_id
            else:
                return "Error: " + str(page['errmsg'])
