#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from depsys.sysconfig import ProjectConfig, UserConfig


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

    def repository(self):
        pass

    def email(self):
        pass

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