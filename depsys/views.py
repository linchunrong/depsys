#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import app
from depsys.model import User,Project
from flask_login import login_user,logout_user,login_required,LoginManager,current_user
from depsys.forms import LoginForm

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.init_app(app)

@app.route('/')
def hello_world():
    return 'Hello World!!'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method == 'POST':
        user = User.query.filter_by(username=form.username.data).first()
        if user.checkUser(user.username,form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password! ')
    if form.username.data == None:
        form.username.data = ''
    return render_template('login.html',form=form,title='Login')