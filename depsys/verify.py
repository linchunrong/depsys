#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, git
from depsys.sysconfig import ProjectConfig, UserConfig
from depsys import sendmsg


class Verify:
    """Form data verify"""
    def ansible(self, path):
        """Ansible available verify"""
        command = path.strip() + "/ansible --version"
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # example of p.stdout.read(), it's bytes
        # b"ansible 2.4.2.0\n  config file = /etc/ansible/ansible.cfg\n  ....
        ansible_version = p.stdout.read().decode('utf-8').split('\n')[0]
        error = p.stderr.read().decode('utf-8').strip('\n')

        if ansible_version:
            return "Version: " + ansible_version
        if error:
            return "Error: " + error

    def repository(self, username, password, address):
        """Connect repository test, only for gitlab currently"""
        repo_address = address.strip()
        if not repo_address:
            return "Error: Repository address is empty!"
        if (not repo_address.startswith('http')) or (not repo_address.endswith('.git')):
            return "Error: Repository should be start with http and end with .git!"
        if (not username.strip()) or (not password):
            return "Error: Username/Password is required!"
        auth_info = username.strip() + ":" + password
        # add username/password in repo address
        repo_address = repo_address.replace("://", "://" + auth_info + "@")
        g = git.cmd.Git()
        try:
            # run command like: git ls-remote http://user:pwd@addres
            g.ls_remote(repo_address)
        except Exception as Err:
            error = str(Err.stderr)
            # remove auth info from stderr
            error = error.replace(auth_info + '@', '')
            return "Error: " + error
        else:
            return "Connect repository success!"

    def email(self,receiver):
        """Send mail test"""
        subject = "Send mail test"
        content = "Send by Depsys, if you receive this, that means email work."
        try:
            sendmsg.email(receiver=receiver, subject=subject, content=content)
        except Exception as Err:
            return str(Err)
        else:
            return "Email sent"

    def project_name(self, project_name):
        """Project name valid verify"""
        if project_name.strip() == "":
            return "Error: Project name is empty!"
        conf = ProjectConfig()
        exist = conf.get(project_name=project_name)
        if exist:
            return "Error: Project name already exist!"
        else:
            return "This name is valid!"

    def username(self, username):
        """Username valid verify"""
        if username.strip() == "":
            return "Error: Username is empty!"
        conf = UserConfig()
        exist = conf.get(username=username)
        if exist:
            return "Error: Username already exist!"
        else:
            return "This name is valid!"
