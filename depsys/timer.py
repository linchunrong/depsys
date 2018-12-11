#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from depsys import prepares


def write_time(**kwargs):
    current_time = time.localtime()
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
    time_file = prepares.temp_path.joinpath('user_time_%s' % str(kwargs.get('user_id')))
    with open(time_file, 'w') as info:
        info.write("%s %s %s" % (current_time, kwargs.get('user_add'), kwargs.get('browser_version')))


def pick_time(user_id):
    return user_id


#def fun_timer():
#    app.logger.info('Hello timer!')
#    global timer
#    timer = threading.Timer(5.5, fun_timer)
#    timer.start()


#timer = threading.Timer(1, fun_timer)
#timer.start()
