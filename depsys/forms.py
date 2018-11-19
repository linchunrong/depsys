#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators, \
    SelectField, TextAreaField, RadioField, BooleanField


class LoginForm(FlaskForm):
    """Login Form"""
    username = StringField('Username', validators=[validators.InputRequired()])
    password = PasswordField('Password', validators=[validators.InputRequired()])
    # remember_me = BooleanField('Remember me')
    submit = SubmitField('登录')


class UserForm(FlaskForm):
    """User Form"""
    username = StringField('Username', validators=[validators.InputRequired(message="用户名必填！")])
    password = PasswordField('Password', validators=[validators.EqualTo('confirm', message="密码不一致！")])
    confirm = PasswordField('Repeat Password')
    enable = BooleanField('Enable', default=True)
    role = RadioField('Role', choices=[('admin', '管理员 <em>(admin)</em>'),
                                       ('editor', '维护者 <em>(editor)</em>'),
                                       ('user', '一般用户 <em>(user)</em>')], default='user')
    submit = SubmitField('保存')


class ProfileForm(FlaskForm):
    """Profile Form"""
    password = PasswordField('New Password', validators=[validators.EqualTo('confirm', message="密码不一致！")])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('更新')


class ProjectForm(FlaskForm):
    """Project Form"""
    project_name = StringField('Project_name', validators=[validators.InputRequired(message="工程名必填!")])
    servers = StringField('IPs', validators=[validators.InputRequired(message="服务器地址必填!")])
    group = RadioField('Group', choices=[('研发1部', '研发1部'),
                                         ('研发2部', '研发2部'),
                                         ('研发3部', '研发3部'),
                                         ('研发4部', '研发4部')], default='研发1部')
    source_address = StringField('Repository_address')
    describe = StringField('Describe', validators=[validators.InputRequired(message="项目描述必填！")])
    project_type = RadioField('Project_type', choices=[('zip', 'zip'),
                                                       ('war', 'war'),
                                                       ('jar', 'jar')], default='zip')
    post_script_type = SelectField('Post_script_type', choices=[('shell', 'shell script'),
                                                                ('python', 'python script')], default='shell')
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
    mail_address = StringField('Mail_address')
    smtp_user = StringField('Smtp_user')
    smtp_password = PasswordField('Smtp_pwd')
    submit = SubmitField('保存')


class ReportForm(FlaskForm):
    """Report Form"""
    media_email = BooleanField('<strong>邮件 </strong><em>(请于下方选择收件人)</em>', default=True)
    media_wechat = BooleanField('<strong>微信 </strong><em>(版本发布公众号)</em>', default=True)
    receiver = SelectField('Receiver', choices=[('operate@cmbfae.com', '系统运行部'),
                                                ('cmbfae-it@cmbfae.com', '信息技术部')], default='operate@cmbfae.com')
    date_range = RadioField('Date_range', choices=[('7', '最近七天'),
                                                   ('1', '今天')], default='7')
    submit = SubmitField('发送')
