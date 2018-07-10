#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import app, socketio

if __name__ == '__main__':
    #app.run(debug=True)
    socketio.run(app,debug=True)
