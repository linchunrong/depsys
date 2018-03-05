#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys import app
from depsys.model import User,Project

@app.route('/')
def hello_world():
    return 'Hello World!!'