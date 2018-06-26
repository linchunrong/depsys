#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, time, os, random, string, pathlib
from threading import Lock
from depsys import socketio
from flask_socketio import disconnect, emit
from depsys.sysconfig import SystemConfig

# deploy execute process
thread = None
thread_lock = Lock()
temp_path = "tmp"


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
    while True:
        socketio.sleep(3)
        socketio.emit('my_response',
                      {'time_stamp': time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()), 'data': str(create_playbook())},
                      namespace='/execute')


def my_path():
    """Get current file path"""
    root = os.path.dirname(os.path.realpath(__file__))
    root = pathlib.Path(root)
    return root


def mkdir(path):
    path = path.strip()
    os.chdir(my_path())
    isExists = os.path.exists(path)
    if isExists:
        # print (path +  "目录已存在！")
        return False
    else:
        os.makedirs(path)
        # print (path + "创建成功！")
        return True


def random_string(num):
    """Generate num-bit random sting"""
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, int(num)))
    return ran_str


def get_script():
    """Base on sysconfig, make the script local"""
    conf = SystemConfig()
    remote_script = conf.get().deploy_script
    # check if script path is set in remote http url
    if 'http' in remote_script:
        os.chdir(my_path())
        local_script = temp_path + "/deploy_script.sh"
        urllib.request.urlretrieve(remote_script, filename=local_script)
        return str(local_script)
    # otherwise, script path is set in local path by default
    else:
        local_script = remote_script
        return str(local_script)


def create_playbook():
    """Create ansible playbook"""
    os.chdir(my_path())
    mkdir(temp_path)
    src_file = my_path()/"yml/execute.yml"
    #file_name = "playbook_" + random_string(16) + ".yml"
    file_name = "playbook.yml"
    with open(src_file) as src:
        playbook_template = src.read()
    os.chdir(temp_path)
    with open(file_name, 'w+') as dest:
        dest.write(playbook_template.replace("local_script_path", get_script()))
        playbook = dest.read()
    return playbook
