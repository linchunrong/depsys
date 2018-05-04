#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import app,db
from depsys.model.User import User,Certif,System
from depsys.dashboard import dashboard_index
from depsys.deploy import deploy_index
from flask import render_template, redirect, url_for, flash, request,session,jsonify
from depsys.forms import LoginForm, ConfigForm
from flask_login import login_user, login_required, logout_user

# Index
@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm()
    if form.validate_on_submit() and request.method=='POST':
        user=User.query.filter_by(username=form.username.data).first()
        if user is None:
            error = 'Invalid username'
        elif user.password != form.password.data:
            error = 'Invalid password'
        else:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html',form=form,title='登录', error=error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/deploy')
@login_required
def deploy():
    project_list = deploy_index()
    return render_template('deploy.html', project_list=project_list)

@app.route('/deploy/<project>')
@login_required
def project_deploy(project):
    return render_template('deploy_project.html',project=project)

@app.route('/config')
@login_required
def config():
    return render_template('sysconfig.html')

@app.route('/config/<project>')
@login_required
def project_config(project):
    form = ConfigForm()
    return render_template('config_project.html',project=project, form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return ("Still working on it...")

@app.route('/dashboard/<project>')
@login_required
def project_dashboard(project):
    return ("Still working on it...")

# json data pages
@app.route('/deploy_num')
@login_required
def deploy_num():
    data = dashboard_index()
    return jsonify(data)