#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import db
from depsys.models import Project

def system_config():
    pass

def project_config(project_name_old, project_name, servers, source_address, post_script_type, post_script):
    """Update project config"""
    if project_name_old != None:
        update_project = Project.query.filter_by(project_name=project_name_old).first()
        update_project.project_name = project_name
        update_project.servers = servers
        update_project.source_address = source_address
        update_project.post_script_type = post_script_type
        update_project.post_script = post_script
        db.session.commit()
    else:
        add_project = Project(project_name=project_name,servers=servers,source_address=source_address,post_script_type=post_script_type,post_script=post_script)
        db.session.add(add_project)
        db.session.commit()