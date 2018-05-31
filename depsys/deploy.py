#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys.models import Project, Record

def deploy_index():
    project_list = []
    project_info = Project.query.all()
    for i in range(len(project_info)):
        project_list.append(project_info[i].project_name)

    return project_list

def deploy_record(project):
    """Get deployed record"""
    p_id = Project.query.filter_by(project_name=project).first().project_id
    items = Record.query.filter_by(project_id=p_id).all()
    return items