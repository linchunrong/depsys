#!/usr/bin/env python
# -*- coding: utf-8 -*-

# network setting
Host = '0.0.0.0'
Port = 5000

# Set it True for Test env, False for Prod env
DEBUG = True

SECRET_KEY = '\x84\x96\x04\xe9\xc5\xe1\xb4\xc5\xa4M\xcd\x9a\xf4b"\xce\x88\xe36\x88c\x13\xe5\t'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://depsys:123456@127.0.0.1:3306/depsys'

# default admin user/password
admin_user = 'admin'
admin_pass = '888888'

# package path and owner
DEPLOY_PKG_PATH = '/home/FaeWork/pkgs/'
PKG_OWNER = 'FaeWork'

# with args in this file which info come from git commit, file should under gitlab root path
EXTRA_ARGS_FILE = "release_note.json"

# date paths, which save project data, would be ./depsys/data_path
data_path = 'data'
# temporary path, would be ./depsys/temp_path
temp_path = 'tmp'
# bin path, not in use, would be ./depsys/bin_path
bin_path = 'bin'

# WeChat interface
API_URL = 'https://qyapi.weixin.qq.com/cgi-bin/'
corpid = '******'
corpsecret = '******'
AgentId = '******'
