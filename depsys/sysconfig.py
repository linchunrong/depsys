#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import db
from depsys.models import Project, System, User

class System_config:
    """System config, only have update method"""
    def update(self, ansible_path, deploy_script, start_script, stop_script, repository_server, repository_user, repository_password, smtp_server, smtp_user, smtp_password):
        # Should be only one record in DB
        item = System.query.first()
        item.ansible_path = ansible_path
        item.deploy_script = deploy_script
        item.start_script = start_script
        item.stop_script = stop_script
        item.repository_server = repository_server
        item.repository_user = repository_user
        item.repository_pwd = repository_password
        item.smtp_server = smtp_server
        item.smtp_user = smtp_user
        item.smtp_password = smtp_password
        db.session.commit()
        db.session.close()

class Project_config:
    """Action for project"""
    def update(self,project_name_old, project_name, servers, source_address, post_script_type, post_script):
        """Update project config"""
        item = Project.query.filter_by(project_name=project_name_old).first()
        item.project_name = project_name
        item.servers = servers
        item.source_address = source_address
        item.post_script_type = post_script_type
        item.post_script = post_script if post_script else None
        db.session.commit()
        db.session.close()

    def add(self, project_name, servers, source_address, post_script_type, post_script):
        """Add project"""
        item = Project(project_name=project_name, servers=servers, source_address=source_address,
                              post_script_type=post_script_type, post_script=post_script if post_script else None)
        db.session.add(item)
        db.session.commit()
        db.session.close()

    def delete(self, project_name):
        """Delete project"""
        if project_name:
            item = Project.query.filter_by(project_name=project_name).first()
            db.session.delete(item)
            db.session.commit()
            db.session.close()

class User_config:
    """Config for user"""
    def update(self, user_id, password):
        """Update user info"""
        # Add more arguments if need
        item = User.query.filter_by(id=user_id).first()
        item.password = password
        db.session.commit()
        db.session.close()