#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from depsys import app,db
from depsys.model.User import User,Certif,System
from depsys.dashboard import dashboard_index
from depsys.deploy import deploy_index
from flask import render_template, redirect, url_for, flash, request,session,jsonify

def login_need(func):
    @wraps(func)
    def login_check(*args, **kwargs):
        if 'username' in session:
            return func(*args,**kwargs)
        else:
            #flash('Please login first!')
            return redirect(url_for('login'))
    return login_check

# Index
@app.route('/')
@app.route('/index')
@login_need
def index():
    return render_template('index.html')

# Login
@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=request.form['username']).first()
        #passwd = User.query.filter_by(password=request.form['password']).first()
        passwd = user.password

        if user is None:
            error = 'Invalid username'
        elif passwd != password:
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

@app.route('/deploy')
@login_need
def deploy():
    project_list = deploy_index()
    return render_template('deploy.html', project_list=project_list)

@app.route('/deploy/<project>')
@login_need
def project_deploy(project):
    return ("Still working on it...")

@app.route('/config')
@login_need
def config():
    return ("Still working on it...")

@app.route('/config/<project>')
@login_need
def project_config(project):
    return ("Still working on it...")

@app.route('/dashboard')
@login_need
def dashboard():
    return ("Still working on it...")

@app.route('/dashboard/<project>')
@login_need
def project_dashboard(project):
    return ("Still working on it...")

# json data pages
@app.route('/deploy_num')
@login_need
def deploy_num():
    data = dashboard_index()
    return jsonify(data)