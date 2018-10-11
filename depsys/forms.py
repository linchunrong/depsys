#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators, SelectField, TextAreaField, RadioField, BooleanField


class LoginForm(FlaskForm):
    """Login Form"""
    username = StringField('Username', validators=[validators.InputRequired()])
    password = PasswordField('Password', validators=[validators.InputRequired()])
    # remember_me = BooleanField('Remember me')
    submit = SubmitField('登录')


class UserForm(FlaskForm):
    """User change password"""
    password = PasswordField('New Password', validators=[validators.EqualTo('confirm', message="密码不一致！")])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('更新')


class ProjectForm(FlaskForm):
    """Project Form"""
    project_name = StringField('Project_name', validators=[validators.InputRequired(message="工程名必填!")])
    servers = StringField('IPs', validators=[validators.InputRequired(message="服务器地址必填!")])
    # source_address = StringField('Repository_address', validators=[validators.InputRequired(message="源码地址必填！")])
    source_address = StringField('Repository_address')
    project_type = RadioField('Project_type', choices=[('zip', 'zip'), ('war', 'war'), ('jar', 'jar')], default='zip')
    post_script_type = SelectField('Post_script_type', choices=[('shell', 'shell script'), ('python', 'python script')], default='shell')
    post_script = TextAreaField('Post_script')
    submit = SubmitField('保存')


class SystemForm(FlaskForm):
    """System Form"""
    ansible_path = StringField('Ansible_path', validators=[validators.InputRequired(message="Ansible 运行路径必填！")])
    deploy_script = StringField('Deploy_script', validators=[validators.InputRequired(message="发布脚本路径必填！")])
    start_script = StringField('Start_script', validators=[validators.InputRequired(message="启动脚本路径必填！")])
    stop_script = StringField('Stop_script', validators=[validators.InputRequired(message="停止脚本路径必填！")])
    repository_server = StringField('Repository_server', validators=[validators.InputRequired(message="源码服务器路径必填！")])
    repository_user = StringField('Rep_user', validators=[validators.InputRequired(message="源码库用户必填！")])
    repository_password = PasswordField('Rep_pwd')
    smtp_server = StringField('Smtp_server')
    smtp_user = StringField('Smtp_user')
    smtp_password = PasswordField('Smtp_pwd')
    submit = SubmitField('保存')


class ReportForm(FlaskForm):
    """Report Form"""
    media_email = BooleanField('<strong>邮件 </strong><em>(请于下方选择收件人)</em>', default=True)
    media_wechat = BooleanField('<strong>微信 </strong><em>(版本发布公众号)</em>', default=True)
    receiver = SelectField('Receiver', choices=[('operate@cmbfae.com', '系统运行部'), ('cmbfae-it@cmbfae.com', '信息技术部'), ('lincr@cmbfae.com', 'lin')], default='lincr@cmbfae.com')
    date_range = RadioField('Date_range', choices=[('7', '最近七天'), ('1', '今天')], default='7')
    submit = SubmitField('发送')
