#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys.models import Project

def deploy_index():
    project_list = []
    project_info = Project.query.all()
    for i in range(len(project_info)):
        project_list.append(project_info[i].project_name)

    return project_list