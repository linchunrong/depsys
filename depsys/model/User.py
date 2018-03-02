# -*- coding: utf-8 -*-
from depsys import db

class User(db.Model):
    __tablename__ = 'user'
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