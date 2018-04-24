#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import db, login_manager
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(16),unique=True,nullable=False)
    password = db.Column(db.String(24),nullable=False)
    group = db.Column(db.String(36))
    enable = db.Column(db.Boolean,default=True,nullable=False)
    permission = db.Column(db.Integer)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def __init__(self,username,password):
        self.username  = username
        self.password = password
    def __repr__(self):
        return '<User %r>' % self.username

class Certif(db.Model):
    __tablename__ = 'certif'
    cert_id = db.Column(db.Integer,primary_key=True)
    cert_name = db.Column(db.String(16),nullable=False)
    password = db.Column(db.String(24),nullable=False)
    interface = db.Column(db.String(16))

    def __init__(self,cert_name,password):
        self.cert_name = cert_name
        self.password = password
    def __repr__(self):
        return  '<Cert %r>' % self.cert_name

class System(db.Model):
    __tablename__ = 'system'
    id = db.Column(db.Integer,primary_key=True)
    # auth: local, ldap etc.
    auth = db.Column(db.String(16),default='local',nullable=False)
    ansible_path = db.Column(db.String(200))
    deploy_script = db.Column(db.String(200))
    start_script = db.Column(db.String(200))
    stop_script = db.Column(db.String(200))
    smtp_server = db.Column(db.String(50))
    smtp_user = db.Column(db.String(24))
    smtp_pwd = db.Column(db.String(24))

    def __init__(self,auth):
        self.auth = auth
    def __repr__(self):
        return '<Auth %r>' % self.auth