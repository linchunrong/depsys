#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess


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

    def project(self):
        pass