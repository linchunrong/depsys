#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, os
from depsys import app, bases


def write_time(**kwargs):
    """Write the newest user request info into a temp file"""
    # asctime will take localtime as arg by default
    current_time = time.asctime()
    time_file = bases.temp_path.joinpath('%s%s' % (bases.time_file_pre, str(kwargs.get('user_id'))))
    data = {
        "User_id": kwargs.get('user_id'),
        "Username": kwargs.get('username'),
        "Time": current_time,
        "User_add": kwargs.get('user_add'),
        "Browser": kwargs.get('browser_version')
    }
    with open(time_file, 'w') as info:
        info.write(str(data))


def pick_time():
    path = bases.temp_path
    # get files list under temp path
    files = bases.path_files(path)
    for file in files:
        if file.startswith(bases.time_file_pre):
            with open(path.joinpath(file), 'r') as f:
                # turn str to dict
                result = eval(f.read())
                current_time = time.time()
                # turn Time ('Mon Dec 17 09:12:21 2018') format as time.time() (1545009146.0)
                save_time = time.mktime(time.strptime(result.get('Time')))
                time_pass = current_time - save_time
            # session timeout in 30min
            if time_pass > 1800:
                print("User %s logout at %s" % (result.get('Username'), result.get('Time')))
                write_logout(result.get('User_id'))
            # print(result.get('User_id'), result.get('Time'), time_pass)
    # print("Schedule output")


def write_logout(user_id):
    """Write user logout time info into db"""
    ######
    # write db func
    ######
    # remove user request time file, in case logout time duplication
    try:
        os.remove(bases.temp_path.joinpath('%s%s' % (bases.time_file_pre, user_id)))
    except Exception as Err:
        app.logger.error("Failed to remove user time file %s%s due to %s." % (bases.time_file_pre, user_id, str(Err)))
    else:
        app.logger.info("Removed user time file %s%s" % (bases.time_file_pre, user_id))



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
