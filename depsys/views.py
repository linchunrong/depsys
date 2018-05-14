#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_user, login_required, logout_user

from depsys import app
from depsys.dashboard import dashboard_index
from depsys.deploy import deploy_index
from depsys import sysconfig
from depsys.sysconfig import Project_config
from depsys.forms import LoginForm, ConfigForm, SystemForm
from depsys.models import User


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
    form = SystemForm()
    return render_template('sysconfig.html',form=form)

@app.route('/config/<project>', methods=['GET', 'POST'])
@login_required
def project_config(project):
    form = ConfigForm()
    p = Project_config()
    if request.method=="POST":
        if project == "add_new_project":
            #sysconfig.project_config(project_name_old="",project_name=form.project_name.data,servers=form.servers.data,
            #               source_address=form.source_address.data,post_script_type=form.post_script_type.data,post_script=form.post_script.data)
            p.add(project_name=form.project_name.data,servers=form.servers.data,
                           source_address=form.source_address.data,post_script_type=form.post_script_type.data,post_script=form.post_script.data)
        else:
            #sysconfig.project_config(project_name_old=project,project_name=request.form['new_project'],servers=form.servers.data,
            #               source_address=form.source_address.data,post_script_type=form.post_script_type.data,post_script=form.post_script.data)
            p.update(project_name_old=project,project_name=request.form['new_project'],servers=form.servers.data,
                           source_address=form.source_address.data,post_script_type=form.post_script_type.data,post_script=form.post_script.data)
        return redirect(url_for('deploy'))
    return render_template('config_project.html',project=project, form=form)

@app.route('/delete/<project>', methods=['GET', 'POST'])
@login_required
def delete_project(project):
    p = Project_config()
    if request.method=="POST":
        #sysconfig.project_delete(project_name=project)
        p.delete(project_name=project)
        return redirect(url_for('deploy'))
    return render_template('del_project.html',project=project)

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