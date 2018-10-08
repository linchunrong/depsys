#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = '\x84\x96\x04\xe9\xc5\xe1\xb4\xc5\xa4M\xcd\x9a\xf4b"\xce\x88\xe36\x88c\x13\xe5\t'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://depsys:123456@127.0.0.1:3306/depsys'

# default admin user/password
admin_user = 'admin'
admin_pass = '888888'

DEPLOY_PKG_PATH = '/home/FaeWork/pkgs/'
PKG_OWNER = 'FaeWork'

# with args in this file which info come from git commit, file should under gitlab root path
EXTRA_ARGS_FILE = "release_note.json"

# WeChat interface
API_URL = 'https://qyapi.weixin.qq.com/cgi-bin/'
corpid = '******'
corpsecret = '******'
AgentId = '******'
