#!/usr/bin/env python
# -*- coding: utf-8 -*-

# !!! Only upper can be save into flask app.config object !!!  get value via app.config['key']

# Set it True for Test env, False for Prod env
DEBUG = True

SECRET_KEY = '\x84\x96\x04\xe9\xc5\xe1\xb4\xc5\xa4M\xcd\x9a\xf4b"\xce\x88\xe36\x88c\x13\xe5\t'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://depsys:123456@127.0.0.1:3306/depsys'

# network setting
HOST = '0.0.0.0'
PORT = 5000

# default admin user/password
ADMIN_USER = 'admin'
ADMIN_PASS = '888888'

# package path and owner
DEPLOY_PKG_PATH = '/home/FaeWork/pkgs/'
PKG_OWNER = 'FaeWork'

# with args in this file which info come from git commit, file should under gitlab root path
EXTRA_ARGS_FILE = "release_note.json"

# date paths, which save project data, would be ./depsys/data_path
DATA_PATH = 'data'
# temporary path, would be ./depsys/temp_path
TEMP_PATH = 'tmp'
# bin path, not in use, would be ./depsys/bin_path
BIN_PATH = 'bin'
# logs file name
LOGS_NAME = 'app.log'

# WeChat interface
API_URL = 'https://qyapi.weixin.qq.com/cgi-bin/'
CORPID = '******'
CORPSECRET = '******'
AGENTID = '******'
