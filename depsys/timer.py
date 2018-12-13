#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from depsys import prepares


def write_time(**kwargs):
    current_time = time.localtime()
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
    time_file = prepares.temp_path.joinpath('user_time_%s' % str(kwargs.get('user_id')))
    data = {
        "Time": current_time,
        "User_Add": kwargs.get('user_add'),
        "Browser": kwargs.get('browser_version')
    }
    with open(time_file, 'w') as info:
        info.write(str(data))


def pick_time():
    pass
    # print("Schedule output")


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
