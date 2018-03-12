#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import app,db
from depsys.model.User import User,Certif,System
from depsys.model.Project import Project,Record
from flask import render_template, redirect, url_for, flash, request,session

# Index
@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        projects = Project.query.all()
        records = Record.query
        return render_template('index.html', projects=projects, records=records)
    #flash('Please login first!')
    return redirect(url_for('login'))

# Login
@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=request.form['username']).first()
        passwd = User.query.filter_by(password=request.form['password']).first()

        if user is None:
            error = 'Invalid username'
        elif passwd is None:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            #flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    #flash('You were logged out')
    return redirect(url_for('login'))