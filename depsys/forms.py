#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators, SelectField, TextAreaField

class LoginForm(FlaskForm):
    """Login Form"""
    username = StringField('Username', validators=[validators.InputRequired()])
    password = PasswordField('Password', validators=[validators.InputRequired()])
    #remember_me = BooleanField('Remember me')
    submit = SubmitField('登录')

class ConfigForm(FlaskForm):
    """Config Form"""
    project_name = StringField('Project_name', validators=[validators.InputRequired(message="工程名必填!")])
    servers = StringField('IPs', validators=[validators.InputRequired(message="服务器地址必填!")])
    source_address = StringField('Repository_address', validators=[validators.InputRequired(message="源码地址必填！")])
    post_script_type = SelectField('Post_script_type', choices=[('shell','shell script'),('python','python script')])
    post_script = TextAreaField('Post_script')
    submit = SubmitField('保存')

class SystemForm(FlaskForm):
    """System Form"""
    ansible_path = StringField('Ansible_path', validators=[validators.InputRequired()])
    deploy_script = StringField('Deploy_script', validators=[validators.InputRequired()])
    start_script = StringField('Start_script', validators=[validators.InputRequired()])
    stop_script = StringField('Stop_script', validators=[validators.InputRequired()])
    repository_server = StringField('Repository_server', validators=[validators.InputRequired])
    repository_user = StringField('Rep_user', validators=[validators.InputRequired])
    repository_password = PasswordField('Rep_pwd', validators=[validators.InputRequired])
    smtp_server = StringField('Smtp_server', validators=[validators.InputRequired])
    smtp_user = StringField('Smtp_user', validators=[validators.InputRequired])
    smtp_password = PasswordField('Smtp_pwd', validators=[validators.InputRequired])
    submit = SubmitField('保存')