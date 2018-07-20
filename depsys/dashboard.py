#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys.models import Record, Project
from depsys.sysconfig import ProjectConfig
from depsys import db


class DeployInfo:
    """Get Deploy information"""
    def projects(self):
        """Get all projects"""
        project_list = []
        project_info = Project.query.all()
        for i in range(len(project_info)):
            project_list.append(project_info[i].project_name)
        return project_list

    def status(self):
        """Get deploy status"""
        amount = []
        for status in ('1', '0', '-1'):
            amount.append(len(Record.query.filter_by(status=status).all()))

        data = {
            'amount': amount,
            'status': ['Success', 'Failed', 'Abort']
        }
        return data

    def status_detail(self):
        """Get deploy status info of every project"""
        projects_list = self.projects()
        project_status_list = []
        for project in projects_list:
            project_id = ProjectConfig().get(project).project_id
            amount = []
            for status in ('1', '0', '-1'):
                amount.append(len(Record.query.filter_by(project_id=project_id, status=status).all()))
            project_status_list.append({'project':project, 'Success':amount[0], 'Failed':amount[1], 'Abort':amount[2]})

        data = {
            'status': ['project','Success', 'Failed', 'Abort'],
            'status_info': project_status_list
        }

        return data


class DeployRecord:
    """Record actions for deploy"""
    def add(self, project, status, version, requester, deployer, deploy_reason, time_begin, time_end, logs):
        """Add deployed record"""
        project_id = ProjectConfig().get(project).project_id
        item = Record(project_id=project_id, status=status, version=version, requester=requester if requester else None, deployer=deployer if deployer else None,
                      deploy_reason=deploy_reason if deploy_reason else None, time_begin=time_begin, time_end=time_end, logs=logs)
        db.session.add(item)
        db.session.commit()
        db.session.close()

    def delete(self, project):
        """Delete deployed record"""
        pass

    def get(self, project):
        """Get deployed records"""
        project_id = ProjectConfig().get(project).project_id
        items = Record.query.filter_by(project_id=project_id).all()
        return items
