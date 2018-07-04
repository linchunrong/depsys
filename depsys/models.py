#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import db, login_manager
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(17),unique=True,nullable=False)
    password = db.Column(db.String(24),nullable=False)
    group = db.Column(db.String(36))
    enable = db.Column(db.Boolean,default=True,nullable=False)
    permission = db.Column(db.Integer)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def __repr__(self):
        return '<User %r>' % self.username

class System(db.Model):
    __tablename__ = 'system'
    id = db.Column(db.Integer,primary_key=True)
    # auth: local, ldap etc.
    auth = db.Column(db.String(16),default='local',nullable=False)
    ansible_path = db.Column(db.String(200))
    deploy_script = db.Column(db.String(200))
    start_script = db.Column(db.String(200))
    stop_script = db.Column(db.String(200))
    repository_server = db.Column(db.String(200))
    repository_user = db.Column(db.String(24))
    repository_pwd = db.Column(db.String(24))
    smtp_server = db.Column(db.String(50))
    smtp_user = db.Column(db.String(24))
    smtp_pwd = db.Column(db.String(24))

    def __repr__(self):
        return '<Auth %r>' % self.auth

class Project(db.Model):
    __tablename__ = 'project'
    project_id = db.Column(db.Integer,primary_key=True)
    project_name = db.Column(db.String(16),unique=True,nullable=False)
    group = db.Column(db.String(36))
    servers = db.Column(db.String(100))
    enable = db.Column(db.Boolean,default=True,nullable=False)
    current_version = db.Column(db.String(16))
    source_address = db.Column(db.String(100))
    describe = db.Column(db.String(200))
    type = db.Column(db.String(10))
    # type: shell, python etc.
    post_script_type = db.Column(db.String(10))
    post_script = db.Column(db.String(200))
    records = db.relationship('Record',backref='prjt')

    def __repr__(self):
        return '<Project %r>' % self.project_name

class Record(db.Model):
    __tablename__ = 'record'
    record_id = db.Column(db.Integer,primary_key=True)
    project_id = db.Column(db.Integer,db.ForeignKey('project.project_id'))
    status = db.Column(db.Integer,default=1,nullable=False)
    version = db.Column(db.String(16))
    requester = db.Column(db.String(16))
    deployer = db.Column(db.String(16))
    deploy_reason = db.Column(db.String(200))
    time_begin = db.Column(db.DateTime)
    time_end = db.Column(db.DateTime)
    logs = db.Column(db.TEXT(65535))

    def __repr__(self):
        return '<Record %r>' % self.project_id