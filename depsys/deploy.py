#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, time, os, sys, random, string, pathlib, subprocess, shutil, yaml, json
from threading import Lock
from git import Repo, Git
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
        print("Error: ", str(Err))
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
        extra_file = str(my_pkg[2])
        if os.path.isfile(extra_file):
            with open(extra_file, encoding='utf-8') as logs:
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
                    logs = json.load(logs)
                except Exception as Err:
                    emit('my_response', {'data': "Read " + setting.EXTRA_ARGS_FILE + " failed due to: " + str(Err) + "\n",
                                         'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"})
                    print("Error: ", str(Err))
                    DeployRecord().add(project=project, status=status, version=branch, requester="N/A", deploy_reason="N/A", deployer="N/A",
                                       time_begin=time_begin, time_end=time_end, logs=logs)
                else:
                    for log in logs['发布列表']:
                        if log['发布版本'] == branch:
                            requester = log['发布人']
                            deploy_reason = log['发布原因']
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
            # save extra args file if exist
            else:
                if os.path.isfile(extra_file):
                    try:
                        shutil.copyfile(extra_file,str(destfile_path.joinpath(setting.EXTRA_ARGS_FILE)))
                    except Exception as e:
                        return ("Failed to save extra args file due to: " + str(e))
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
        emit('my_response',
             {'data': "Found deployed local package, use it for this deployment." + "\n", 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"})
        extra_file = my_path().joinpath(data_path, project, version, setting.EXTRA_ARGS_FILE)
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
                my_remote.pull(version)
            except Exception as Err:
                emit('my_response', {'data': "Download package failed due to: " + str(Err) + "\n", 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"})
                emit('error_exit')
                print("Error: ", str(Err))
                sys.exit(1)
            # write commit info into
            else:
                # os.chdir(str(project_work_path(str(project))))
                # get info from commit log
                # g = Git()
                # commit_info = g.log('-1')
                # with open(setting.EXTRA_ARGS_FILE, 'w+') as info:
                #     info.write(commit_info)
                extra_file = project_work_path(project).joinpath(setting.EXTRA_ARGS_FILE)
            if not os.path.isfile(extra_file):
                extra_file = None
        # use git sparse checkout to get specific files
        else:
            package = project_work_path(project).joinpath(version, package_name)
            # checkout the specific package path
            os.chdir(str(project_work_path(str(project))))
            shell_command = 'git config core.sparseCheckout true && echo "' + version + '" >> .git/info/sparse-checkout'
            subprocess.Popen(shell_command, shell=True)
            # pull specific path via gitPython
            try:
                my_remote = empty_repo.create_remote(project, repo_address)
                my_remote.pull('master')
            except Exception as Err:
                emit('my_response', {'data': "Download package failed due to: " + str(Err) + "\n",
                                     'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime()) + ":"})
                emit('error_exit')
                print("Error: ", str(Err))
                sys.exit(1)
                # write commit info into
            else:
                os.chdir(str(project_work_path(str(project))))
                extra_file = project_work_path(project).joinpath(version, setting.EXTRA_ARGS_FILE)
            if not os.path.isfile(extra_file):
                extra_file = None

        return [str(package), package_name, str(extra_file)]
