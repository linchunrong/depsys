#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wtforms import Form,BooleanField,StringField,SubmitField,TextField,PasswordField,validators

class LoginForm(Form):
    """Login Form"""
    username = StringField('Username', validators=[validators.InputRequired()])
    password = PasswordField('Password', validators=[validators.InputRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')