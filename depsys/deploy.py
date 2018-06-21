#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, time, os
from threading import Lock
from depsys import socketio
from flask_socketio import disconnect, emit
from depsys.sysconfig import SystemConfig

# deploy execute process
thread = None
thread_lock = Lock()


@socketio.on('disconnect_request', namespace='/execute')
def disconnect_request():
    emit('my_response',
         {'time_stamp': time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()), 'data': "Abort!"})
    disconnect()


@socketio.on('connect', namespace='/execute')
def execute_do():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=execute_thread)
    emit('my_response', {'time_stamp': time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()), 'data': "Start!"})


def execute_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(3)
        count += 1
        socketio.emit('my_response',
                      {'time_stamp': time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()), 'data': "Executing..."},
                      namespace='/execute')


def mkdir(path):
    path = path.strip()
    isExists = os.path.exists(path)
    if isExists:
        # print (path +  "目录已存在！")
        return False
    else:
        os.makedirs(path)
        # print (path + "创建成功！")
        return True


def get_script():
    """Base on sysconfig, make the script local"""
    conf = SystemConfig()
    remote_script = conf.get().deploy_script
    # check if script path is set in remote http url
    if 'http' in remote_script:
        path = "tmp"
        mkdir(path)
        local_script = path + "/deploy_script.sh"
        urllib.request.urlretrieve(remote_script, filename=local_script)
        return local_script
    # otherwise, script path is set in local path by default
    else:
        local_script = remote_script
        return local_script
