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
            project_status_list.append([project, amount[0], amount[1], amount[2]])

        data = [['project','Success', 'Failed', 'Abort']]+ project_status_list

        return data

    def top_deploy(self,top_num):
        """Top num deploy project info"""
        project_list = self.projects()
        deploy_num = []
        for project in project_list:
            project_id = ProjectConfig().get(project).project_id
            number = len(Record.query.filter_by(project_id=project_id).all())
            deploy_num.append((project, number))

        deploy_num = sorted(deploy_num, key=lambda num: num[1], reverse=True)
        projects = []
        amount = []
        for child in deploy_num:
            projects.append(child[0])
            amount.append(child[1])

        data = {
            'projects': projects[:-(top_num+1):-1],
            'amount': amount[:-(top_num+1):-1]
        }

        return data

    def top_requester(self,top_num):
        """Top num requester info"""
        requesters =[]
        records = Record.query.all()
        for record in records:
            requesters.append(record.requester)
        # use set to uniq requester
        requester_num = []
        for requester in set(requesters):
            requester_num.append((requester,requesters.count(requester)))

        requester_num = sorted(requester_num, key=lambda num: num[1], reverse=True)
        #requesters_new = []
        amount = []
        for child in requester_num:
            #requesters_new.append(child[0])
            amount.append({'value':child[1], 'name': child[0]})

        data = {
            #'requesters': requesters_new[:-(top_num+1):-1],
            'amount': amount[:-(top_num+1):-1]
        }

        return data


class DeployRecord:
    """Record actions for deploy"""
    def add(self, project, status, version, requester, deployer, deploy_reason, time_begin, time_end, pkg_md5, logs):
        """Add deployed record"""
        project_id = ProjectConfig().get(project).project_id
        # check if record exist, if yes update, else add
        record_exist = Record.query.filter_by(project_id=project_id, version=version).first()
        if record_exist:
            record_exist.status = status
            record_exist.requester = requester if requester else "N/A"
            record_exist.deployer = deployer if deployer else "N/A"
            record_exist.deploy_reason = deploy_reason if deploy_reason else "N/A"
            record_exist.time_begin = time_begin
            record_exist.time_end = time_end
            record_exist.pkg_md5 = pkg_md5
            record_exist.logs = logs
        else:
            record_new = Record(project_id=project_id, status=status, version=version, requester=requester if requester else "N/A", deployer=deployer if deployer else "N/A",
                          deploy_reason=deploy_reason if deploy_reason else "N/A", time_begin=time_begin, time_end=time_end, pkg_md5=pkg_md5, logs=logs)
            db.session.add(record_new)
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
