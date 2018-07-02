#!/usr/bin/env python
from threading import Lock
from flask_socketio import emit, join_room, leave_room, \
    close_room, rooms, disconnect
from depsys import socketio
import time

thread = None
thread_lock = Lock()


@socketio.on('my_event', namespace='/test')
def test_message(message):
    emit('my_response',
         {'data': message['data'], 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime())})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    emit('my_response',
         {'data': message['data'], 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime())},
         broadcast=True)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime())})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime())})


@socketio.on('close_room', namespace='/test')
def close(message):
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime())},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    emit('my_response',
         {'data': message['data'], 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime())},
         room=message['room'])


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    emit('my_response',
         {'data': 'Disconnected!', 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime())})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            emit('my_response', {'data': 'Connected', 'time_stamp': "\n" + time.strftime("%Y-%m-%d:%H:%M:%S",time.localtime())})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

