#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

# call monkey.patch_all to ignore gevent(take care of socketio thread) warning
monkey.patch_all()

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config.from_object('setting')
# app.config.from_envvar('FLASKR_SETTINGS')
socketio = SocketIO(app, async_mode=async_mode)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

from depsys import views
