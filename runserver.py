#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import app, socketio

if __name__ == '__main__':
    #app.run(debug=True)
    socketio.run(app, host='0.0.0.0', debug=True)
