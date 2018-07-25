#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, time, os, sys, random, string, pathlib, subprocess, shutil, yaml
from threading import Lock
from git import Repo
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
workstation = "workstation"


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
    # string room should be "project@branch", pick out project and branch name from it.
    room_split = str(room).split("@")
    project = str(room_split[0])
    branch = str(room_split[1])
    working_path = project_work_path(project)
    # clean the working path
    clean_command = 'rm -rf ' + str(working_path)
    subprocess.Popen(clean_command, shell=True)
    try:
        # get deploy package
        my_pkg = get_package(project=project, version=branch)
        my_hosts = get_hosts(project)
        my_playbook = get_playbook(package_name=str(my_pkg[1]), local_package=str(my_pkg[0]))
    except Exception as Err:
        print ("Error: ", str(Err))
        sys.exit(1)
    # create ansible command
    ansible_bin = SystemConfig().get().ansible_path
    command = ansible_bin + "/ansible-playbook -i " + my_hosts + " " + my_playbook
    # command = "ping www.baidu.com -c 5"
    os.chdir(str(working_path))
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
        # get extra args if exist
        extra_file = my_path().joinpath(working_path,setting.EXTRA_ARGS_FILE)
        if os.path.isfile(extra_file):
            with open(setting.EXTRA_ARGS_FILE, encoding='utf-8') as args:
                # parse EXTRA_ARGES_FILE
                args = yaml.load(args)
                try:
                    requester = args['requester']
                    deploy_reason = args['deploy_reason']
                except Exception as Err:
                    print("Failed to get extra args due to: " + str(Err))
                    DeployRecord().add(project=project, status=status, version=branch, requester="N/A",deploy_reason="N/A", deployer="N/A",
                                       time_begin=time_begin, time_end=time_end, logs=logs)
                DeployRecord().add(project=project, status=status, version=branch, requester=requester, deploy_reason=deploy_reason, deployer="N/A",
                                   time_begin=time_begin, time_end=time_end, logs=logs)
        else:
            DeployRecord().add(project=project, status=status, version=branch, requester="N/A", deploy_reason="N/A", deployer="N/A",
                               time_begin=time_begin, time_end=time_end, logs=logs)
    # save deployed package, str(my_pkg[1]) stand for package name
    if status == 1:
        srcfile = working_path.joinpath(str(my_pkg[1]))
        if os.path.isfile(srcfile):
            destfile_path = my_path().joinpath(data_path, str(project), str(branch))
            mkdir(destfile_path)
            destfile = destfile_path.joinpath(str(my_pkg[1]))
            try:
                shutil.copyfile(str(srcfile),str(destfile))
            except Exception as Err:
                return ("Failed to save deployed package due to: " + str(Err))
        else:
            return ("Deployed package was saved before, this probably a rollback action.")
    else:
        return ("Not a success deployment, package save isn't need.")


def my_path():
    """Get current file path"""
    root = os.path.dirname(os.path.realpath(__file__))
    root = pathlib.Path(root)
    return root


def project_work_path(project):
    """Get current project workstation path"""
    project_path = my_path().joinpath(workstation, project)
    mkdir(project_path)
    return project_path


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


def get_playbook(package_name, local_package):
    """Create ansible playbook"""
    project = package_name.split('.')[0]
    os.chdir(str(project_work_path(str(project))))
    src_file = my_path()/"yml/execute.yml"
    dest_file = "playbook_" + random_string(16) + ".yml"
    # read playbook template =
    with open(src_file) as src:
        playbook_template = src.read()
    # cd to temporary folder and write a temporary playbook
    with open(dest_file, 'w+') as dest:
        content = playbook_template.replace("start_script_file", get_script("start_script"))
        content = content.replace("deploy_script_file", get_script("deploy_script"))
        content = content.replace("stop_script_file", get_script("stop_script"))
        content = content.replace("local_pkg_file", local_package)
        content = content.replace("dest_pkg_file", setting.DEPLOY_PKG_PATH + package_name)
        content = content.replace("pkg_owner", setting.PKG_OWNER)
        dest.write(content)
    return dest_file


def get_hosts(project):
    """Create ansible hosts file"""
    hosts_path = project_work_path(project)
    os.chdir(str(hosts_path))
    file_name = "hosts_" + random_string(16)
    with open(file_name, 'w+') as hosts:
        conf = ProjectConfig()
        hosts_list = conf.get(project).servers.strip().split(',')
        for host in hosts_list:
            hosts.write(host + '\n')
    hosts_file = str(hosts_path.joinpath(file_name))
    return hosts_file


def get_package(project, version):
    """Get package from repository server"""
    os.chdir(str(project_work_path(str(project))))
    conf = ProjectConfig().get(project)
    package_name = project + "." + conf.type
    repo_address = conf.source_address.strip()
    # add username:password into repo address for git auth
    sysconf = SystemConfig().get()
    username = sysconf.repository_user
    password = sysconf.repository_pwd
    if username and password:
        repo_address = repo_address.replace("://", "://" + urllib.parse.quote(username) + ":" + urllib.parse.quote(password) + "@")
    # check if local package exist
    deployed_package = my_path().joinpath(data_path, project, version, package_name)
    if os.path.isfile(deployed_package):
        emit('my_response',
             {'data': "Found deployed local package, use it for this deployment." + "\n", 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"})
        return [str(deployed_package), package_name]
    # get package from remote git
    else:
        # pull package via gitPython
        package = project_work_path(project).joinpath(package_name)
        empty_repo = Repo.init(str(project_work_path(project)))
        try:
            my_remote = empty_repo.create_remote(project, repo_address)
            my_remote.pull(version)
        except Exception as Err:
            emit('my_response', {'data': "Download package failed due to: " + str(Err) + "\n", 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"})
            emit('error_exit')
            print ("Error: ", str(Err))
            sys.exit(1)
        return [str(package), package_name]
