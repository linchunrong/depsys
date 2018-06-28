#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys.models import Record, Project


class DeployInfo:
    """Get all projects"""
    def projects(self):
        project_list = []
        project_info = Project.query.all()
        for i in range(len(project_info)):
            project_list.append(project_info[i].project_name)
        return project_list


    def records(self, project):
        """Get deployed records of project"""
        p_id = Project.query.filter_by(project_name=project).first().project_id
        items = Record.query.filter_by(project_id=p_id).all()
        return items


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
