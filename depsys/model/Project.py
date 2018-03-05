#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import db

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
    records = db.relationship('Record',backref='prjt')

    def __init__(self,project_name,servers,type):
        self.project_name  = project_name
        self.servers = servers
        self.type = type
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
    time_begin = db.Column(db.Time)
    time_end = db.Column(db.Time)
    logs = db.Column(db.String(200))

    def __init__(self,project_id,status):
        self.project_id = project_id
        self.status = status
    def __repr__(self):
        return '<Record %r>' % self.project_id