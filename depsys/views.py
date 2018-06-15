#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, request, jsonify, session
from flask_login import login_user, login_required, logout_user
from depsys import app, execute
from depsys.dashboard import dashboard_index
from depsys.deploy import DeployInfo
from depsys.sysconfig import Project_config, System_config, User_config
from depsys.forms import LoginForm, ConfigForm, SystemForm, UserForm
from depsys.models import User, System, Project


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
    if form.validate_on_submit() and request.method == 'POST':
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            error = 'Invalid username'
        elif user.password != form.password.data:
            error = 'Invalid password'
        else:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', form=form, title='登录', error=error)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    error = None
    form = UserForm()
    user_id = session['user_id']
    user = User.query.filter_by(id=user_id).first()
    if request.method == "POST":
        if form.validate_on_submit():
            u = User_config()
            u.update(user_id=user_id, password=form.password.data if form.password.data else user.password)
            return redirect(url_for('profile'))
        else:
            for key in form.errors:
                error = form.errors[key]
    return render_template('profile.html', form=form, user=user, error=error)


@app.route('/deploy')
@login_required
def deploy_index():
    project_list = DeployInfo().projects()
    return render_template('deploy.html', project_list=project_list)


@app.route('/deploy/<project>')
@login_required
def project_deploy(project):
    records = DeployInfo().records(project)
    return render_template('deploy_project.html', project=project, records=records)


@app.route('/execute/<project>', methods=['POST'])
@login_required
def deploy_exec(project):
    branch = request.form['branch']
    return render_template('execute.html', project=project, branch=branch, async_mode=execute.socketio.async_mode)


@app.route('/config', methods=['GET', 'POST'])
@login_required
def config():
    error = None
    form = SystemForm()
    conf = System.query.first()
    if request.method == "POST":
        if form.validate_on_submit():
            s = System_config()
            s.update(ansible_path=form.ansible_path.data, deploy_script=form.deploy_script.data, start_script=form.start_script.data, stop_script=form.stop_script.data,
                    repository_server=form.repository_server.data, repository_user=form.repository_user.data,
                     repository_password=form.repository_password.data if form.repository_password.data else conf.repository_pwd,
                    smtp_server=form.smtp_server.data, smtp_user=form.smtp_user.data, smtp_password=form.smtp_password.data)
            return redirect(url_for('config'))
        else:
            for key in form.errors:
                error = form.errors[key]
    return render_template('sysconfig.html', form=form, conf=conf, error=error)


@app.route('/config/<project>', methods=['GET', 'POST'])
@login_required
def project_config(project):
    error = None
    form = ConfigForm()
    conf = Project.query.filter_by(project_name=project).first()
    if request.method == "POST":
        if form.validate_on_submit():
            p = Project_config()
            if project == "add_new_project":
                p.add(project_name=form.project_name.data, servers=form.servers.data,
                               source_address=form.source_address.data, post_script_type=form.post_script_type.data, post_script=form.post_script.data)
            else:
                p.update(project_name_old=project, project_name=form.project_name.data, servers=form.servers.data,
                               source_address=form.source_address.data, post_script_type=form.post_script_type.data, post_script=form.post_script.data)
            return redirect(url_for('deploy'))
        else:
            for key in form.errors:
                error = form.errors[key]
    return render_template('config_project.html', project=project, form=form, conf=conf, error=error)


@app.route('/delete/<project>', methods=['GET', 'POST'])
@login_required
def project_delete(project):
    p = Project_config()
    if request.method == "POST":
        p.delete(project_name=project)
        return redirect(url_for('deploy'))
    return render_template('del_project.html', project=project)


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
