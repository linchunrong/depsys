#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setting, urllib.request, urllib.parse, time, os, sys, random, string, pathlib, subprocess, shutil, json, re
from flask import request
from threading import Lock
from git import Repo
from depsys import socketio
from flask_socketio import disconnect, emit, join_room
from depsys.sysconfig import SystemConfig, ProjectConfig
from depsys.dashboard import DeployRecord

# deploy execute process
# thread = None
thread_lock = Lock()
# define variables
data_path = setting.data_path.strip()
bin_path = setting.bin_path.strip()
temp_path = setting.temp_path.strip()
extra_args_file = setting.EXTRA_ARGS_FILE.strip()
deploy_pkg_path = setting.DEPLOY_PKG_PATH.strip()
pkg_owner = setting.PKG_OWNER.strip()
batch_socket_room = "batch_execute"
workstation = "workstation"


@socketio.on('my_event', namespace='/execute')
def message(message):
    emit('my_response',
         {'data': message['data'], 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()) + ":"})


@socketio.on('executing', namespace='/execute')
def executing(message):
    # every thread own their room to get their logs
    with thread_lock:
        join_room(message['room'])
        emit('my_response', {'data': "后台脚本开始执行..." + "\n", 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, room=message['room'])
        # call deploy thread
        socketio.start_background_task(target=execute_thread, info=message['room'], single=True)


@socketio.on('batch_executing', namespace='/execute')
def batch_exec():
    """Func for batch deploy"""
    room = batch_socket_room
    join_room(room)
    emit('my_response', {'data': "Projects version detail refer to file: " + extra_args_file + ", which post in " + SystemConfig().get().repository_server,
                         'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, room=room)
    try:
        batch_list = get_branches(room)
    except Exception as Err:
        emit('my_response', {'data': "Failed to get release list due to: " + str(Err),
                             'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, room=room)
        raise Exception("Get Deploy List Error")
    else:
        emit('my_response', {'data': "Got release list: \n" + str(batch_list),
                             'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, room=room)
        emit('my_response', {'data': "批量发布开始...", 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, room=room)
        for child in batch_list:
            project = child.split('@')[0]
            exist = ProjectConfig().get(project)
            # only when project exist will go on
            if exist:
                # call deploy thread
                with thread_lock:
                    socketio.start_background_task(target=execute_thread, info=child, single=False)
            else:
                emit('my_response', {'data': "[ERROR] [" + project + "] 工程未配置/不存在，请检查！",
                                     'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, room=room)


@socketio.on('disconnect_request', namespace='/execute')
def disconnect_request():
    disconnect()


@socketio.on('connect', namespace='/execute')
def test_connect():
    #global thread
    #with thread_lock:
    #    if thread is None:
    #        thread = socketio.start_background_task(target=execute)
    emit('my_response', {'data': '开始连接后台...', 'time_stamp': time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()) + ":"})


@socketio.on('disconnect', namespace='/execute')
def print_disconnect():
    print('Client disconnected', request.sid)


def execute_thread(info, single=True):
    """Execute process thread"""
    time_begin = time.localtime()
    # string info should be "project@branch", pick out project and branch name from it.
    info_split = str(info).split("@")
    project = str(info_split[0])
    branch = str(info_split[1])
    working_path = project_work_path(project)
    # clean the working path
    clean_command = 'rm -rf ' + str(working_path)
    subprocess.Popen(clean_command, shell=True)
    time.sleep(2)
    try:
        # get deploy package
        my_pkg = get_package(project=project, version=branch, room=info)
        my_hosts = get_hosts(project)
        my_playbook = get_playbook(package_name=str(my_pkg[1]), local_package=str(my_pkg[0]))
    except Exception as Err:
        sys.exit(str(Err))

    # define room name, which use for socket output info
    if single:
        room = info
    else:
        room = batch_socket_room

    # create ansible command
    ansible_bin = SystemConfig().get().ansible_path
    command = ansible_bin + "/ansible-playbook -i " + my_hosts + " " + my_playbook
    # command = "ping www.baidu.com -c 5"
    os.chdir(str(working_path))
    logs_name = "logs_" + random_string(16) + ".txt"
    logs_file = str(working_path.joinpath(logs_name))
    # run ansible and write logs into temporary log files
    with open(logs_file, "w+") as file:
        proc = subprocess.Popen(command, shell=True, stdout=file)

    # read out the log file and send to frontend
    with open(logs_file) as logs:
        running = True
        while running:
            socketio.sleep(2)
            output = str(logs.read())
            # only print out when there's output and single release, single should be false when batch deploy
            if output and single:
                socketio.emit('my_response', {'time_stamp': "", 'data': output}, namespace='/execute', room=room)
            # poll() func will get return code of subrocess.Popen(), None means running
            if proc.poll() != None:
                running = False
                time_end = time.localtime()
                socketio.emit('my_response', {'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()) + ":",
                                              'data': "[" + project + "] 发布脚本执行完毕!"}, namespace='/execute', room=room)
    # write logs into record
    with open(logs_file) as logs:
        logs = logs.read()
        # change return code for status, 0 for successful termination, >0 for termination with an error code, <0 if was killed
        returncode = proc.poll()
        if returncode == 0:
            status = 1
            socketio.emit('my_response', {'data': "[" + project + "] 发布成功，请检查进程是否正常！",
                                          'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"},
                          namespace='/execute', room=room)
        elif returncode <0:
            status = -1
            socketio.emit('my_response', {'data': "[" + project + "] 发布中断！！",
                                          'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"},
                          namespace='/execute', room=room)
        else:
            status = 0
            socketio.emit('my_response', {'data': "[ERROR] [" + project + "] 发生错误，请检查日志！",
                                          'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"},
                      namespace='/execute', room=room)
        # grab package md5 from logs
        search_line = '''md5_value.stdout_lines": \[\n ([^>]+) ]'''
        result = re.compile(search_line).findall(logs)
        # example of result:  "11706132cfe495581a63c1f9d30241a4", need to cut down ""
        pkg_md5 = result[0].strip()[1:-1]
        # get extra args if exist
        extra_file = str(my_pkg[2])
        if os.path.isfile(extra_file):
            with open(extra_file, encoding='utf-8') as release_info:
                # parse json format
                # logs template
                #{
                #    "发布列表": [{
                #        "发布原因": "B2b个人会员微信入会需求",
                #        "发布人": "伍磊",
                #        "发布工程名称": "b2b-open-auth.war",
                #        "发布版本": "20180808_1800",
                #        "发布类型": "功能优化"
                #    }, {
                #        "发布原因": "B2b个人会员微信入会需求",
                #        "发布人": "伍磊",
                #        "发布工程名称": "b2b-busi.war",
                #        "发布版本": "20180808_1801   功能优化",
                #        "发布类型": "功能优化"
                #    }
                #}
                try:
                    release_info = json.load(release_info)
                except Exception as Err:
                    socketio.emit('my_response', {'data': "[" + project + "] Read " + extra_args_file + " failed due to: " + str(Err) + "\n",
                                         'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, namespace='/execute', room=room)
                    print("Error: ", str(Err))
                    DeployRecord().add(project=project, status=status, version=branch, requester="N/A", deploy_reason="N/A", deployer="N/A",
                                       time_begin=time_begin, time_end=time_end, pkg_md5=pkg_md5, logs=logs)
                else:
                    for info in release_info['发布列表']:
                        if info['发布版本'] == branch:
                            requester = info['发布人']
                            deploy_reason = info['发布原因']
                            DeployRecord().add(project=project, status=status, version=branch, requester=requester, deploy_reason=deploy_reason, deployer="N/A",
                                   time_begin=time_begin, time_end=time_end, pkg_md5=pkg_md5, logs=logs)
        else:
            DeployRecord().add(project=project, status=status, version=branch, requester="N/A", deploy_reason="N/A", deployer="N/A",
                               time_begin=time_begin, time_end=time_end, pkg_md5=pkg_md5, logs=logs)
    # save deployed package, str(my_pkg[1]) stand for package name
    if status == 1:
        srcfile = my_pkg[0]
        destfile_path = my_path().joinpath(data_path, str(project), str(branch))
        destfile = destfile_path.joinpath(str(my_pkg[1]))
        if os.path.isfile(srcfile) and srcfile != str(destfile):
            mkdir(destfile_path)
            try:
                shutil.copyfile(str(srcfile),str(destfile))
            except Exception as Err:
                return ("[" + project + "] Failed to save deployed package due to: " + str(Err))
            # save extra args file if exist
            else:
                if os.path.isfile(extra_file):
                    try:
                        shutil.copyfile(extra_file,str(destfile_path.joinpath(extra_args_file)))
                    except Exception as e:
                        return ("[" + project + "] Failed to save extra args file due to: " + str(e))
        else:
            return ("[" + project + "] Deployed package was saved before, this probably a rollback action.")
    else:
        return ("[" + project + "] Not a success deployment, package save isn't need.")


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
        raise Exception("Wrong Script Name Error")
    '''
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
    '''
    return str(remote_script)


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
        content = playbook_template.replace("start_script_file", "curl -s " + get_script("start_script") + " | sh -s " + str(project))
        content = content.replace("deploy_script_file","curl -s " + get_script("deploy_script") + " | sh -s " + str(project))
        content = content.replace("stop_script_file", "curl -s " + get_script("stop_script") + " | sh -s " + str(project))
        content = content.replace("local_pkg_file", local_package)
        content = content.replace("dest_pkg_file", deploy_pkg_path + package_name)
        content = content.replace("pkg_owner", pkg_owner)
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


def get_package(project, version, room):
    """Get package from repository server"""
    os.chdir(str(project_work_path(str(project))))
    conf = ProjectConfig().get(project)
    package_name = project + "." + conf.type
    # use system config if project don't have specific repo
    if conf.source_address:
        repo_address = conf.source_address.strip()
    else:
        repo_address = SystemConfig().get().repository_server.strip()
    # add username:password into repo address for git auth
    sysconf = SystemConfig().get()
    username = sysconf.repository_user
    password = sysconf.repository_pwd
    if username and password:
        repo_address = repo_address.replace("://", "://" + urllib.parse.quote(username) + ":" + urllib.parse.quote(password) + "@")
    # check if local package exist
    deployed_package = my_path().joinpath(data_path, project, version, package_name)
    if os.path.isfile(deployed_package):
        socketio.emit('my_response', {'data': "[" + project + "] Found deployed local package, use it for this deployment." + "\n",
                    'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, namespace='/execute', room=room)
        extra_file = my_path().joinpath(data_path, project, version, extra_args_file)
        if not os.path.isfile(extra_file):
            extra_file = None
        return [str(deployed_package), package_name, str(extra_file)]
    # get package from remote git
    else:
        empty_repo = Repo.init(str(project_work_path(project)))
        # if project has a specific repo, let's take care of the whole branch
        if conf.source_address:
            package = project_work_path(project).joinpath(package_name)
            # pull package via gitPython
            try:
                my_remote = empty_repo.create_remote(project, repo_address)
                socketio.emit('my_response', {'data': "[" + project + "] Downloading package from gitlab..." + "\n",
                            'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, namespace='/execute', room=room)
                my_remote.pull(version)
            except Exception as Err:
                socketio.emit('my_response', {'data': "[ERROR] [" + project + "] Download package from repository failed, please check your setting! \n",
                            'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, namespace='/execute', room=room)
                print("Error: ", str(Err))
                raise Exception("Package Download Error")
            # write commit info into
            else:
                extra_file = project_work_path(project).joinpath(extra_args_file)
            if not os.path.isfile(extra_file):
                extra_file = None
        # use git sparse checkout to get specific files
        else:
            package = project_work_path(project).joinpath(version, package_name)
            # checkout the specific package path
            os.chdir(str(project_work_path(str(project))))
            shell_command = 'git config core.sparseCheckout true && echo "' + version + '" >> .git/info/sparse-checkout && echo "' \
                            + extra_args_file + '" >> .git/info/sparse-checkout'
            subprocess.Popen(shell_command, shell=True)
            # pull specific path via gitPython
            try:
                my_remote = empty_repo.create_remote(project, repo_address)
                socketio.emit('my_response', {'data': "[" + project + "] Downloading package from gitlab..." + "\n",
                            'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, namespace='/execute', room=room)
                my_remote.pull('master')
            except Exception as Err:
                socketio.emit('my_response', {'data': "[ERROR] [" + project + "] Download package from repository failed, please check your setting! \n",
                            'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, namespace='/execute', room=room)
                print("Error: ", str(Err))
                raise Exception("Package Download Error")
            else:
                # we maybe check out empty package folder via sparse checkout
                if os.path.isfile(package):
                    extra_file = project_work_path(project).joinpath(extra_args_file)
                else:
                    socketio.emit('my_response', {'data': "[ERROR] [" + project + "] Seems this version doesnt' include a package, please check!" + "\n",
                                'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"}, namespace='/execute', room=room)
                    raise Exception("Version Empty Error")
            if not os.path.isfile(extra_file):
                extra_file = None

        return [str(package), package_name, str(extra_file)]


def get_branches(room):
    """Get projects & branches list"""
    # using temp path as work path
    working_path = my_path().joinpath(temp_path, 'batch')
    # clean the working path
    clean_command = 'rm -rf ' + str(working_path)
    subprocess.Popen(clean_command, shell=True)
    time.sleep(2)
    mkdir(working_path)
    os.chdir(str(working_path))
    # get repository address
    sysconf = SystemConfig().get()
    repo_address = sysconf.repository_server.strip()
    username = sysconf.repository_user
    password = sysconf.repository_pwd
    # add username:password into repo address for git auth
    if username and password:
        repo_address = repo_address.replace("://", "://" + urllib.parse.quote(username) + ":" + urllib.parse.quote(password) + "@")
    # get extra_args_file
    empty_repo = Repo.init(str(working_path))
    # update config to check out extra_args_file only
    shell_command = 'git config core.sparseCheckout true && echo "' + extra_args_file + '" >> .git/info/sparse-checkout'
    subprocess.Popen(shell_command, shell=True)
    # pull specific path via gitPython
    try:
        my_remote = empty_repo.create_remote("batch", repo_address)
        socketio.emit('my_response', {'data': "Downloading " + extra_args_file + " from repository...",
                                      'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"},
                      namespace='/execute', room=room)
        my_remote.pull('master')
    except Exception as Err:
        socketio.emit('my_response', {'data': "[ERROR] Download " + extra_args_file + " from repository failed, please check your setting!",
                                      'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"},
                      namespace='/execute', room=room)
        print("Error: ", str(Err))
        raise Exception("File Download Error")
    else:
        socketio.emit('my_response', {'data': "Saved " + extra_args_file + " to " + str(working_path),
                                      'time_stamp' : "\n" + time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime()) + ":"},
                      namespace='/execute', room=room)
        with open(extra_args_file, encoding='utf-8') as release_info:
            # release_info is a json format file
            try:
                release_info = json.load(release_info)
            except Exception as Err:
                socketio.emit('my_response', {'data': "Read " + extra_args_file + " failed due to: " + str(Err),
                                              'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"},
                              namespace='/execute', room=room)
                print("Error: ", str(Err))
                raise Exception("Read File Error")
            else:
                batch_list = []
                for info in release_info['发布列表']:
                    # use split cut down project type
                    project = info['发布工程名称'].strip().split('.')[:-1][0]
                    branch = info['发布版本'].strip()
                    project_branch = project + '@' + branch
                    batch_list.append(project_branch)
                # sample of batch_list - ['isp_finance@20180820_1500', 'isp-forward@20180820_1501', 'isp_web@20180820_1502']
                return batch_list
