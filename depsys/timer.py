#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, os
from depsys import app, bases
from depsys.sysconfig import AuditConfig


def write_time(**kwargs):
    """Write the newest user request info into a temp file"""
    data = {
        "User_id": kwargs.get('user_id'),
        "Username": kwargs.get('username'),
        # asctime will take localtime as arg by default
        "Time": time.asctime(),
        "User_addr": kwargs.get('user_addr'),
        "Browser": kwargs.get('browser_version')
    }
    # in case user login via different browser, create file for every browser
    file_name = '%s_%s_%s' % (bases.time_file_pre, str(kwargs.get('user_id')), data.get('Browser'))
    time_file = bases.temp_path.joinpath(file_name)
    with open(time_file, 'w') as info:
        info.write(str(data))


def read_time(file):
    """Read out time file data, and turn to dict"""
    with open(file, 'r') as f:
        # turn str to dict
        result = eval(f.read())
        data = {
            "User_id": result.get('User_id'),
            "Username": result.get('Username'),
            "Time": time.strptime(result.get('Time')),
            "User_addr": result.get('User_addr'),
            "Browser": result.get('Browser'),
        }

    return data


def pick_time():
    path = bases.temp_path
    # get files list under temp path
    files = bases.path_files(path)
    for file in files:
        if file.startswith(bases.time_file_pre):
            # read out data from file
            data = read_time(bases.temp_path.joinpath(file))
            current_time = time.time()
            # turn Time ('Mon Dec 17 09:12:21 2018') format as time.time() (1545009146.0)
            last_time = time.mktime(data.get('Time'))
            # depend on session time out second
            if current_time - last_time > 1800:
                app.logger.info("User %s logout at %s" % (data.get('Username'), time.asctime(data.get('Time'))))
                # add action into data
                data["Action"] = "Logout"
                write_audit(data=data)
    # print("Schedule output")


def write_audit(data):
    """Write user audit info into db"""
    action = data.get('Action')
    user_id = data.get('User_id')
    if action == 'Login':
        file_name = '%s_%s_%s' % (bases.time_file_pre, user_id, data.get('Browser'))
        # if file exist, that means the last logout haven't been wrote
        exist = os.path.isfile(bases.temp_path.joinpath(file_name))
        if exist:
            last_data = read_time(bases.temp_path.joinpath(file_name))
            last_data["Action"] = "Logout"
            # write the last logout
            do_write(data=last_data)
            remove_file(file_name=file_name)
    # write the audit
    do_write(data=data)
    if action == 'Logout':
        file_name = '%s_%s_%s' % (bases.time_file_pre, user_id, data.get('Browser'))
        remove_file(file_name=file_name)


def do_write(data):
    """Do the writing action"""
    audit = AuditConfig()
    try:
        # data is a dict args
        audit.add(user_id=data.get('User_id'), username=data.get('Username'), time_stamp=data.get('Time'),
                  user_addr=data.get('User_addr'), browser=data.get('Browser'), action=data.get('Action'))
    except Exception as Err:
        app.logger.error("Failed to write audit info to db due to: %s" % str(Err))
        raise Exception("Audit data write DB Error")


def remove_file(file_name):
    # remove user request time file, in case data duplication
    try:
        os.remove(bases.temp_path.joinpath(file_name))
    except Exception as Err:
        app.logger.error("Failed to remove user time file %s due to %s" % (file_name, str(Err)))
    else:
        app.logger.info("Removed user time file %s" % file_name)


'''
import threading

def pick_stop(signum, frame):
    global pick
    pick.cancel()


def pick_time():
    global pick
    pick = threading.Timer(5, pick_time)
    pick.start()

signal.signal(signal.SIGINT, pick_stop)
pick_time()
'''
