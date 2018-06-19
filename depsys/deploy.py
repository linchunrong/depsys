#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, time
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


def get_script():
    """Base on sysconfig, make the script local"""
    conf = SystemConfig()
    remote_script = conf.get().deploy_script
    local_script = urllib.urlretieve(remote_script, filename="deploy_script.sh")
    return local_script
