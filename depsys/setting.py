#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = '\x84\x96\x04\xe9\xc5\xe1\xb4\xc5\xa4M\xcd\x9a\xf4b"\xce\x88\xe36\x88c\x13\xe5\t'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://depsys:123456@127.0.0.1:3306/depsys'


DEPLOY_PKG_PATH = '/home/FaeWork/pkg/'
PKG_OWNER = 'FaeWork'

# ymal format file, under branch root path by default
EXTRA_ARGS_FILE = "info.yml"