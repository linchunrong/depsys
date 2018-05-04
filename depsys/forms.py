#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, PasswordField, validators, SelectField, TextAreaField

class LoginForm(FlaskForm):
    """Login Form"""
    username = StringField('Username', validators=[validators.InputRequired()], render_kw={"placeholder": "用户名"})
    password = PasswordField('Password', validators=[validators.InputRequired()], render_kw={"placeholder": "密码"})
    #remember_me = BooleanField('Remember me')
    #submit = SubmitField('Login')

class ConfigForm(FlaskForm):
    """Config Form"""
    project_name = StringField('Project_name', validators=[validators.InputRequired()], render_kw={"placeholder": "请输入新工程名(必填)"})
    servers = StringField('IPs', validators=[validators.InputRequired()], render_kw={"placeholder": "多个IP请以 \",\" 号分隔！(必填)", "style": "width: 60%"})
    source_address = StringField('Repository_address', validators=[validators.InputRequired()], render_kw={"style": "width: 60%"})
    deploy_script = StringField('Deploy_script', validators=[validators.InputRequired()], render_kw={"style": "width: 60%"})
    start_script = StringField('Start_script', validators=[validators.InputRequired()], render_kw={"style": "width: 60%"})
    stop_script = StringField('Stop_script', validators=[validators.InputRequired()], render_kw={"style": "width: 60%"})
    post_script_type = SelectField('Post_script_type', choices=[('shell','shell script'),('python','python script')])
    post_script = TextAreaField('Post_script', render_kw={"placeholder": "请在此框输入完整脚本！", "style": "width: 80%; height: 50px" })
    #submit = SubmitField('Save')
