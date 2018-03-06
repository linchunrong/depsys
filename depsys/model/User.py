#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(16),unique=True,nullable=False)
    password = db.Column(db.String(24),nullable=False)
    group = db.Column(db.String(36))
    enable = db.Column(db.Boolean,default=True,nullable=False)
    permission = db.Column(db.Integer)

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
    auth = db.Column(db.String(16),default='local',nullable=False)

    def __init__(self,auth):
        self.auth = auth
    def __repr__(self):
        return '<Auth %r>' % self.auth