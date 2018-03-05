#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user,logout_user,login_required,LoginManager,current_user

app = Flask(__name__)
app.config.from_object('depsys.setting')
#app.config.from_envvar('FLASKR_SETTINGS')

db = SQLAlchemy(app)

from depsys import views