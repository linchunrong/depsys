#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import BooleanField,StringField,SubmitField,PasswordField,validators

class LoginForm(FlaskForm):
    """Login Form"""
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')