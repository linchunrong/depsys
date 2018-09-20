#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = '\x84\x96\x04\xe9\xc5\xe1\xb4\xc5\xa4M\xcd\x9a\xf4b"\xce\x88\xe36\x88c\x13\xe5\t'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://depsys:123456@127.0.0.1:3306/depsys'


DEPLOY_PKG_PATH = '/home/FaeWork/pkgs/'
PKG_OWNER = 'FaeWork'

# with args in this file which info come from git commit, file should under gitlab root path
EXTRA_ARGS_FILE = "release_note.json"

# WeChat interface
API_URL = 'https://qyapi.weixin.qq.com/cgi-bin/'
corpid = 'wxd5b7127792af7a87'
corpsecret = '3HiF997xDje54TS5Oyy2acN4Xdh2kP2FU49LG0OzwRE'
AgentId = '1000003'
