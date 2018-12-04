#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import logging, os, pathlib

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

# define logfile under app path
parent_path = os.path.dirname(os.path.dirname(__file__))
parent_path = pathlib.Path(parent_path)
logfile = str(parent_path.joinpath('app.log'))
# logs output to app.log via logging module
handler = logging.FileHandler(logfile, encoding='UTF-8')
logging_format = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(filename)s %(funcName)s(%(lineno)s): %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)

from depsys import views

# when use gunicorn runserver:app run this app, combine app logger/gunicorn logger
# if __name__ != '__main__':
#     gunicorn_logger = logging.getLogger('gunicorn.error')
#     app.logger.handlers = gunicorn_logger.handlers
#     app.logger.setLevel(gunicorn_logger.level)
