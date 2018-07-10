#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, time, os, random, string, pathlib, subprocess
from threading import Lock
from depsys import socketio
from flask_socketio import disconnect, emit, join_room
from depsys.sysconfig import SystemConfig, ProjectConfig
from depsys.dashboard import DeployRecord

# deploy execute process
thread = None
thread_lock = Lock()
temp_path = "tmp"
logs_path = "logs"


@socketio.on('my_event', namespace='/execute')
def message(message):
    emit('my_response',
         {'data': message['data'], 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()) + ":"})


@socketio.on('executing', namespace='/execute')
def executing(message):
    # every thread own their room to get their logs
    join_room(message['room'])
    emit('my_response', {'data': "后台脚本开始执行..." + "\n", 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"})
    # call deploy thread
    execute_thread(message['room'])


@socketio.on('disconnect_request', namespace='/execute')
def disconnect_request():
    emit('my_response',
         {'data': '后台已退出!', 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()) + ":"})
    disconnect()


@socketio.on('connect', namespace='/execute')
def connect():
    global thread
    with thread_lock:
        if thread is None:
            emit('my_response', {'data': '开始连接后台...', 'time_stamp': time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()) + ":"})


@socketio.on('disconnect', namespace='/execute')
def print_disconnect():
    print('Client disconnected')


def execute_thread(room):
    """Execute process thread"""
    time_begin = time.localtime()
    os.chdir(str(my_path()))
    mkdir(logs_path)
    os.chdir(logs_path)
    # create ansible command
    # command = "ansible-playbook -i " + get_hosts(project) + " " + get_playbook()
    command = "ping www.baidu.com -c 5"
    logs_file = "logs_" + random_string(16) + ".txt"
    # run ansible and write logs into temporary log files
    with open(logs_file, "w+") as file:
        proc = subprocess.Popen(command, shell=True, stdout=file)

    # read out the log file and send to frontend
    with open(logs_file) as logs:
        running = True
        while running:
            socketio.sleep(2)
            output = str(logs.read())
            # only print out when there's output
            if output:
                emit('my_response', {'time_stamp': "", 'data': output},namespace='/execute', room=room)
            # poll() func will get return code of subrocess.Popen(), None means running
            if proc.poll() != None:
                running = False
                time_end = time.localtime()
                emit('my_response', {'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()) + ":", 'data': "脚本执行完毕!"}, namespace='/execute', room=room)
    emit('script_done', namespace='/execute')

    # write logs into record, string room should be "project@branch", pick out project name from it.
    room_split = str(room).split("@")
    project = room_split[0]
    branch = room_split[1]
    with open(logs_file) as logs:
        logs = logs.read()
        # change return code for status, 0 for successful termination, >0 for termination with an error code, <0 if was killed
        returncode = proc.poll()
        if returncode == 0:
            status = 1
        elif returncode <0:
            status = -1
        else:
            status = 0
        DeployRecord().add(project=project, status=status, version=branch, requester=None, deploy_reason=None, deployer=None,
                           time_begin=time_begin, time_end=time_end, logs=logs)


def my_path():
    """Get current file path"""
    root = os.path.dirname(os.path.realpath(__file__))
    root = pathlib.Path(root)
    return root


def mkdir(path):
    path = path.strip()
    os.chdir(str(my_path()))
    exists = os.path.exists(path)
    if exists:
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
        os.chdir(str(my_path()))
        local_script = temp_path + "/deploy_script.sh"
        urllib.request.urlretrieve(remote_script, filename=local_script)
        return str(local_script)
    # otherwise, script path is set in local path by default
    else:
        local_script = remote_script
        return str(local_script)


def get_playbook():
    """Create ansible playbook"""
    os.chdir(str(my_path()))
    mkdir(temp_path)
    src_file = my_path()/"yml/execute.yml"
    dest_file = "playbook_" + random_string(16) + ".yml"
    # read playbook template =
    with open(src_file) as src:
        playbook_template = src.read()
    # cd to temporary folder and write a temporary playbook
    os.chdir(temp_path)
    with open(dest_file, 'w+') as dest:
        content = playbook_template.replace("local_script_path", get_script())
        dest.write(content)
    # read out the temporary playbook for executing
    #with open(dest_file) as new:
    #    playbook = new.read()

    return dest_file


def get_hosts(project):
    """Create ansible hosts file"""
    os.chdir(str(my_path()))
    mkdir(temp_path)
    file_name = "hosts_" + random_string(16)
    os.chdir(temp_path)
    with open(file_name, 'w+') as hosts:
        conf = ProjectConfig()
        content = conf.get(project).servers
        hosts.write(content)
    hosts_file = str(my_path().joinpath(temp_path, file_name))
    return hosts_file

def get_package(project, version):
    """Get package from repository server"""
    p_repo = ProjectConfig().get(project).source_address
    s_conf = SystemConfig()
    repo = p_repo if p_repo else s_conf.get().repository_server
    remote_pkg = repo + "/" + version
    os.chdir(str(my_path()))
    package = temp_path +  "/" + version
    urllib.request.urlretrieve(remote_pkg, filename=package)
    return str(package)
