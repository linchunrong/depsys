#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, request, jsonify, session
from flask_login import login_user, login_required, logout_user
from depsys import app, message
from depsys.dashboard import DeployInfo, DeployRecord
from depsys.sysconfig import ProjectConfig, SystemConfig, UserConfig
from depsys.forms import LoginForm, ConfigForm, SystemForm, UserForm, ReportForm


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
        user = UserConfig().get(username=form.username.data)
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
    user = UserConfig().get(user_id=user_id)
    if request.method == "POST":
        if form.validate_on_submit():
            u = UserConfig()
            u.update(user_id=user_id, password=form.password.data if form.password.data else user.password)
            return redirect(url_for('profile'))
        else:
            for key in form.errors:
                error = form.errors[key]
    return render_template('profile.html', form=form, user=user, error=error)


@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects(info=None):
    project_list = DeployInfo().projects()
    form = ReportForm()
    if request.method == "POST":
        if form.validate_on_submit():
            info = message.email(receiver=form.receiver.data)
    return render_template('projects.html', project_list=project_list, form=form, info=info)


@app.route('/deploy/<project>')
@login_required
def project_deploy(project,error=None):
    records = DeployRecord().get(project)
    return render_template('deploy_project.html', project=project, records=records, error=error)


@app.route('/execute/<project>', methods=['POST'])
@login_required
def deploy_exec(project):
    from depsys import deploy
    branch = request.form['branch']
    if not branch:
        error = "请输入发版分支！"
        return project_deploy(project=project, error=error)
    return render_template('execute.html', project=project, branch=branch, async_mode=deploy.socketio.async_mode)


@app.route('/config', methods=['GET', 'POST'])
@login_required
def config():
    error = None
    form = SystemForm()
    conf = SystemConfig().get()
    if request.method == "POST":
        if form.validate_on_submit():
            s = SystemConfig()
            if conf:
                s.update(ansible_path=form.ansible_path.data, deploy_script=form.deploy_script.data, start_script=form.start_script.data, stop_script=form.stop_script.data,
                        repository_server=form.repository_server.data, repository_user=form.repository_user.data,
                        repository_password=form.repository_password.data if form.repository_password.data else conf.repository_pwd,
                        smtp_server=form.smtp_server.data, smtp_user=form.smtp_user.data, smtp_password=form.smtp_password.data)
            else:
                s.add(ansible_path=form.ansible_path.data, deploy_script=form.deploy_script.data, start_script=form.start_script.data, stop_script=form.stop_script.data,
                        repository_server=form.repository_server.data, repository_user=form.repository_user.data, repository_password=form.repository_password.data,
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
    conf = ProjectConfig().get(project)
    if request.method == "POST":
        if form.validate_on_submit():
            p = ProjectConfig()
            if project == "add_new_project":
                p.add(project_name=form.project_name.data, servers=form.servers.data, source_address=form.source_address.data,
                      project_type=form.project_type.data, post_script_type=form.post_script_type.data, post_script=form.post_script.data)
            else:
                p.update(project_name_old=project, project_name=form.project_name.data, servers=form.servers.data,
                         source_address=form.source_address.data, project_type=form.project_type.data, post_script_type=form.post_script_type.data, post_script=form.post_script.data)
            return redirect(url_for('projects'))
        else:
            for key in form.errors:
                error = form.errors[key]
    return render_template('config_project.html', project=project, form=form, conf=conf, error=error)


@app.route('/delete/<project>', methods=['GET', 'POST'])
@login_required
def project_delete(project):
    # p = ProjectConfig()
    if request.method == "POST":
        # forbidden project delete until RBAC func done
        # p.delete(project_name=project)
        return redirect(url_for('projects'))
    return render_template('del_project.html', project=project)


@app.route('/charts')
@login_required
def charts():
    return render_template('charts.html')


# json data pages
@app.route('/deploy_num')
@login_required
def deploy_num():
    info = DeployInfo()
    data = info.status()
    return jsonify(data)


@app.route('/deploy_detail')
@login_required
def deploy_detail():
    info = DeployInfo()
    data = info.status_detail()
    return jsonify(data)


@app.route('/deploy_top')
@login_required
def deploy_top():
    info = DeployInfo()
    data = info.top_deploy(10)
    return jsonify(data)


@app.route('/requester_top')
@login_required
def requester_top():
    info = DeployInfo()
    data = info.top_requester(10)
    return jsonify(data)


@app.route('/license')
def license():
    return render_template('license.html')