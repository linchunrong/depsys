#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from depsys.sysconfig import UserConfig, RoleConfig
from flask_login import current_user
from flask import render_template


def get_current_user_role_id():
    item = UserConfig().get(username=current_user.username)
    role_id = item.role

    return role_id


def get_current_user_role():
    role_id = get_current_user_role_id()
    item = RoleConfig().get(role_id=role_id)
    role = item.name

    return role


def deny_response():
    return render_template('deny.html')


# write a decorate for view page
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if get_current_user_role() not in roles:
                return deny_response()
            return f(*args, **kwargs)
        return wrapped
    return wrapper
