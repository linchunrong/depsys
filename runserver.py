#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import app, socketio
from setting import *

if __name__ == '__main__':
    # app.run(debug=True), run app
    socketio.run(app, host=HOST, port=PORT, debug=DEBUG)
