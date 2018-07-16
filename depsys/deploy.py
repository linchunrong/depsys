#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, time, os, sys, random, string, pathlib, subprocess
from threading import Lock
from depsys import socketio, setting
from flask_socketio import disconnect, emit, join_room
from depsys.sysconfig import SystemConfig, ProjectConfig
from depsys.dashboard import DeployRecord

# deploy execute process
thread = None
thread_lock = Lock()
temp_path = "tmp"
logs_path = "logs"
data_path = "data"
bin_path = "bin"


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


@socketio.on('disconnect_exit', namespace='/execute')
def disconnect_exit():
    emit('my_response',
         {'data': "[ERROR] 发生错误，退出！", 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()) + ":"})
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
    # string room should be "project@branch", pick out project and branch name from it.
    room_split = str(room).split("@")
    project = room_split[0]
    branch = room_split[1]
    # get deploy package
    try:
        my_hosts = get_hosts(project)
        my_pkg = get_package(project=project, version=branch)
        my_playbook = get_playbook("deploy_script.sh", package_name=str(my_pkg[1]), local_package=str(my_pkg[0]))
    except Exception as Err:
        print ("Error: ", Err)
        sys.exit(1)
    # create ansible command
    command = "ansible-playbook -i " + my_hosts + " " + my_playbook
    # command = "ping www.baidu.com -c 5"
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
    # write logs into record
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


def get_script(script_type):
    """Base on sysconfig, make the script local"""
    conf = SystemConfig()
    # check script type
    if script_type == "start_script":
        remote_script = conf.get().start_script
    elif script_type == "deploy_script":
        remote_script = conf.get().deploy_script
    elif script_type == "stop_script":
        remote_script = conf.get().stop_script
    else:
        print ("Get script failed! Only support start_script/deploy_script/stop_script.")
        sys.exit(1)
    # fetch script name
    script_name = remote_script.strip().split("/")[-1]
    # check if script path is set in remote http url
    if 'http' in remote_script:
        os.chdir(str(my_path()))
        mkdir(bin_path)
        local_script = my_path().joinpath(bin_path,script_name)
        try:
            urllib.request.urlretrieve(remote_script, filename=str(local_script))
        except Exception as Err:
            sys.exit(Err)
        return str(local_script)
    # otherwise, script path is set in local path by default
    else:
        local_script = remote_script
        return str(local_script)


def get_playbook(script_name, package_name, local_package):
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
        content = playbook_template.replace("start_script_file", get_script("start_script"))
        content = content.replace("deploy_script_file", get_script("deploy_script"))
        content = content.replace("stop_script_file", get_script("stop_script"))
        content = content.replace("local_pkg_file", local_package)
        content = content.replace("dest_pkg_file", setting.DEPLOY_PKG_PATH + package_name)
        content = content.replace("pkg_owner", setting.PKG_OWNER)
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
    p_conf = ProjectConfig().get(project)
    s_conf = SystemConfig().get()
    p_repo = p_conf.source_address
    repo = p_repo if p_repo else s_conf.repository_server
    package_name = project + "." + p_conf.type
    remote_pkg = repo + "/" + version + "/" + package_name
    os.chdir(str(my_path()))
    package_path = my_path().joinpath(data_path, project, version)
    mkdir(package_path)
    package = package_path.joinpath(package_name)
    try:
        urllib.request.urlretrieve(remote_pkg, filename=package)
    except Exception as Err:
        emit('my_response', {'data': "Download package failed due to: " + str(Err) + "\n", 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"})
        # check if local package exist
        if os.path.isfile(package):
            emit('my_response', {'data': "Found local package, use if for deployment." + "\n", 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"})
        else:
            emit('error_exit')
            sys.exit(Err)
    return [str(package), package_name]
