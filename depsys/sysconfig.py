#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from depsys import db
from depsys.models import Project, System, User, Role


class SystemConfig:
    """System config, include get and update method"""
    def update(self, ansible_path, deploy_script, start_script, stop_script,
               repository_server, repository_user, repository_password, smtp_server, mail_address, smtp_user, smtp_password):
        """Update system config"""
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
        item.mail_address = mail_address
        item.smtp_user = smtp_user
        item.smtp_pwd = smtp_password
        db.session.commit()
        db.session.close()

    def add(self,ansible_path, deploy_script, start_script, stop_script,
            repository_server, repository_user, repository_password, smtp_server, mail_address, smtp_user, smtp_password):
        """Add system config"""
        item = System(ansible_path=ansible_path, deploy_script=deploy_script, start_script=start_script, stop_script=stop_script,
                      repository_server=repository_server, repository_user=repository_user, repository_pwd=repository_password,
                      smtp_server=smtp_server, mail_address=mail_address, smtp_user=smtp_user, smtp_pwd=smtp_password)
        db.session.add(item)
        db.session.commit()
        db.session.close()

    def get(self):
        """Get system config"""
        item = System.query.first()
        return item


class ProjectConfig:
    """Action for project"""
    def update(self,project_name_old, project_name, group, describe, servers, source_address, project_type, post_script_type, post_script):
        """Update project config"""
        item = Project.query.filter_by(project_name=project_name_old).first()
        item.project_name = project_name
        item.group = group
        item.describe = describe
        item.servers = servers
        item.source_address = source_address
        item.type = project_type
        item.post_script_type = post_script_type
        item.post_script = post_script
        db.session.commit()
        db.session.close()

    def add(self, project_name, group, describe, servers, source_address, project_type, post_script_type, post_script):
        """Add project"""
        item = Project(project_name=project_name, group=group, describe=describe, servers=servers, source_address=source_address,
                       type=project_type, post_script_type=post_script_type, post_script=post_script)
        db.session.add(item)
        db.session.commit()
        db.session.close()

    def delete(self, project_name):
        """Delete project"""
        item = Project.query.filter_by(project_name=project_name).first()
        db.session.delete(item)
        db.session.commit()
        db.session.close()

    def get(self, project_name):
        """Get project config"""
        item = Project.query.filter_by(project_name=project_name).first()
        return item


class UserConfig:
    """Config for user"""
    def update(self, user_id, password):
        """Update user info"""
        # Add more arguments if need
        item = User.query.filter_by(id=user_id).first()
        item.password = password
        db.session.commit()
        db.session.close()

    def add(self, username, password, role, group=None, enable=1):
        """Add user info"""
        item = User(username=username, password=password, group=group, enable=enable, role=role)
        db.session.add(item)
        db.session.commit()
        db.session.close()

    def delete(self, user_id=None, username=None):
        """Delete user info"""
        if user_id:
            item = User.query.filter_by(id=user_id).first()
        elif username:
            item = User.query.filter_by(username=username).first()
        else:
            print("Error: Either user_id or username as arguments!")
            raise Exception("Delete User: Username/ID Error")
        db.session.delete(item)
        db.session.commit()
        db.session.close()

    def get(self, user_id=None, username=None):
        """Get user info"""
        if user_id:
            item = User.query.filter_by(id=user_id).first()
        elif username:
            item = User.query.filter_by(username=username).first()
        else:
            print("Error: Either user_id or username as arguments!")
            raise Exception("Get User: Username/ID Error")

        return item

    def get_all(self):
        """Get all users info"""
        item = User.query.all()
        return item


class RoleConfig:
    """Config for role"""
    def add(self, name, describe):
        """Add role"""
        item = Role(name=name, describe=describe)
        db.session.add(item)
        db.session.commit()
        db.session.close()

    def delete(self, name):
        """Delete role"""
        item = Role.query.filter_by(name=name).first()
        db.session.delete(item)
        db.session.commit()
        db.session.close()

    def get(self, role_id):
        """Get role config"""
        item = Role.query.filter_by(role_id=role_id).first()
        return item

    def get_all(self):
        """Get all roles"""
        item = Role.query.all()
        return item
