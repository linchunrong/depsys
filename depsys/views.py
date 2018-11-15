#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from flask import render_template, redirect, url_for, request, jsonify, session, flash
from flask_login import login_user, login_required, logout_user
from depsys import app, sendmsg, makemsg
from depsys.dashboard import DeployInfo, DeployRecord
from depsys.sysconfig import *
from depsys.forms import *
from depsys.permissions import requires_roles


# Index
@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method == 'POST':
        user = UserConfig().get(username=form.username.data)
        if user and user.enable:
            if user.password != form.password.data:
                flash("Invalid password")
            else:
                login_user(user)
                return redirect(url_for('index'))
        else:
            flash('Invalid Username')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have logout!")
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    user_id = session['user_id']
    user = UserConfig().get(user_id=user_id)
    role = RoleConfig().get(role_id=user.role)
    if request.method == "POST":
        if form.validate_on_submit():
            if form.password.data:
                u = UserConfig()
                u.update(user_id=user_id, password=form.password.data if form.password.data else user.password)
                flash("密码已更改！")
            else:
                flash("密码无变动！")
        else:
            for key in form.errors:
                flash("Error: " + form.errors[key][0])
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form, user=user, role=role)


@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    project_list = ProjectConfig().get_all()
    form = ReportForm()
    if request.method == "POST" and form.validate_on_submit():
        report = makemsg.Report()
        records = report.get_records(int(form.date_range.data))
        content = report.make_html(records)
        # form.media_email.data/form.media_wechat.data should be True or False
        if form.media_email.data:
            subject = '最近' + form.date_range.data + '天发布记录 GENERATED AT ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # sendmsg.email should return True or Error
            send_mail = sendmsg.email(receiver=form.receiver.data, subject=subject, content=content, subtype='html')
            if send_mail == True:
                flash("Email report sent!")
            else:
                flash(send_mail)
        if form.media_wechat.data:
            pdf_file = report.make_pdf(content, 'deploy_report.pdf')
            text_msg = 'Dear team，今晚所有工程发布完毕，\n请对应的团队开始验证业务！！\n以下是最近' + form.date_range.data + '天发布报表，请查阅。'
            send_wechat_text = sendmsg.wechat('text', message=text_msg)
            if send_wechat_text == True:
                flash("WeChat msg sent!")
            else:
                flash(send_wechat_text)
            send_wechat_file = sendmsg.wechat('file', post_file=pdf_file)
            if send_wechat_file == True:
                flash("WeChat pdf report sent!")
            else:
                flash(send_wechat_file)
        if not form.media_email.data and not form.media_wechat.data:
            flash("Error: 请选择（邮件/微信）至少一个!")
        return redirect(url_for('projects'))

    return render_template('projects.html', project_list=project_list, form=form)


@app.route('/deploy/<project>')
@login_required
def project_deploy(project):
    records = DeployRecord().get(project)
    return render_template('deploy_project.html', project=project, records=records)


@app.route('/execute/<project>', methods=['POST'])
@login_required
@requires_roles('admin', 'editor')
def deploy_exec(project):
    from depsys import deploy
    branch = request.form['branch']
    if not branch:
        flash("请输入发版分支！")
        return redirect(url_for('project_deploy', project=project))
    return render_template('execute.html', project=project, branch=branch, async_mode=deploy.socketio.async_mode)


@app.route('/execute/batch')
@login_required
@requires_roles('admin', 'editor')
def deploy_batch():
    from depsys import deploy
    return render_template('execute.html', project='batch', async_mode=deploy.socketio.async_mode)


@app.route('/config', methods=['GET', 'POST'])
@login_required
@requires_roles('admin', 'editor')
def config():
    form = SystemForm()
    conf = SystemConfig().get()
    if request.method == "POST":
        if form.validate_on_submit():
            s = SystemConfig()
            if conf:
                s.update(ansible_path=form.ansible_path.data.strip(), deploy_script=form.deploy_script.data.strip(), start_script=form.start_script.data.strip(), stop_script=form.stop_script.data.strip(),
                        repository_server=form.repository_server.data.strip(), repository_user=form.repository_user.data.strip(),
                        repository_password=form.repository_password.data if form.repository_password.data else conf.repository_pwd,
                        smtp_server=form.smtp_server.data.strip(), mail_address=form.mail_address.data.strip(), smtp_user=form.smtp_user.data.strip(), smtp_password=form.smtp_password.data)
            else:
                s.add(ansible_path=form.ansible_path.data.strip(), deploy_script=form.deploy_script.data.strip(), start_script=form.start_script.data.strip(), stop_script=form.stop_script.data.strip(),
                        repository_server=form.repository_server.data.strip(), repository_user=form.repository_user.data.strip(), repository_password=form.repository_password.data,
                        smtp_server=form.smtp_server.data.strip(), mail_address=form.mail_address.data.strip(), smtp_user=form.smtp_user.data.strip(), smtp_password=form.smtp_password.data)
            flash("配置已保存！")
        else:
            for key in form.errors:
                flash("Error: "+ form.errors[key][0])
        return redirect(url_for('config'))
    return render_template('sysconfig.html', form=form, conf=conf)


@app.route('/users', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def users():
    if request.method == 'POST':
        # get variable from frontend
        action = request.form['action']
        user_id = request.form['user_id']
        conf = UserConfig()
        if action == 'del_user':
            conf.delete(user_id=user_id)
        if action == 'pwd_reset':
            password = request.form['password']
            conf.update(user_id=user_id, password=password)
        if action == 'enable_change':
            enable = request.form['enable']
            # turn enable to bool type since the value of enable is string true/false
            enable =  True if enable.lower() == 'true' else False
            conf.update(user_id=user_id, enable=enable)
    # method is Get, return all users and roles to page
    user_list = UserConfig().get_all()
    role_list = RoleConfig().get_all()
    return render_template('users.html', user_list=user_list, role_list=role_list)


@app.route('/users/add', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_user():
    form = UserForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if form.password.data:
                conf = UserConfig()
                exist = conf.get(username=form.username.data.strip())
                if exist:
                    flash("Error: 用户已存在！")
                else:
                    role_id = RoleConfig().get(name=form.role.data).role_id
                    conf.add(username=form.username.data.strip(), password=form.password.data.strip(), enable=form.enable.data, role=role_id)
                    flash("用户已增加！")
            else:
                flash("Error: 密码不能为空！" )
        else:
            for key in form.errors:
                flash("Error: " + form.errors[key][0])
        return redirect(url_for('add_user'))
    return render_template('add_user.html', form=form)


@app.route('/config/<project>', methods=['GET', 'POST'])
@login_required
@requires_roles('admin', 'editor')
def project_config(project):
    form = ProjectForm()
    conf = ProjectConfig().get(project)
    if request.method == "POST":
        if form.validate_on_submit():
            p = ProjectConfig()
            project_name = form.project_name.data.strip()
            exist = p.get(project_name)
            if project == "add_new_project":
                if exist:
                    flash("Error: " + project_name + " 已经存在！")
                    return redirect(url_for('project_config', project=project))
                else:
                    p.add(project_name=project_name, group=form.group.data.strip(), describe=form.describe.data.strip(),
                        servers=form.servers.data.strip(), source_address=form.source_address.data.strip(),
                        project_type=form.project_type.data, post_script_type=form.post_script_type.data, post_script=form.post_script.data)
                    flash("添加工程 "+ form.project_name.data.strip() + " 成功！")
                    return redirect(url_for('project_config', project=project_name))
            else:
                # if project name change and new name already exist
                if project != project_name and exist:
                    flash("Error: " + project_name + " 已经存在！")
                    return redirect(url_for('project_config', project=project))
                else:
                    p.update(project_name_old=project, project_name=project_name, group=form.group.data.strip(), describe=form.describe.data.strip(),
                            servers=form.servers.data.strip(), source_address=form.source_address.data.strip(),
                            project_type=form.project_type.data, post_script_type=form.post_script_type.data, post_script=form.post_script.data)
                    flash("工程 " + form.project_name.data.strip() + " 配置已更新！")
                    return redirect(url_for('project_config', project=project_name))
        else:
            for key in form.errors:
                flash("Error: " + form.errors[key][0])
        return redirect(url_for('project_config', project=project))
    return render_template('config_project.html', project=project, form=form, conf=conf)


@app.route('/delete/<project>', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def project_delete(project):
    p = ProjectConfig()
    if request.method == "POST":
        p.delete(project_name=project)
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
