#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys.models import Project, Record
from threading import Lock
from depsys import socketio
from flask import session
from flask_socketio import disconnect, emit


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


thread = None
thread_lock = Lock()


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(3)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/execute')


@socketio.on('disconnect_request', namespace='/execute')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/execute')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})
