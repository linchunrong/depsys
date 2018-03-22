#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bokeh.charts import Bar, output_file, show
from bokeh.embed import components
from depsys.model.Project import Record,Project
from flask import render_template

def dash_index():
    projects = Project.query.all()
    amount = []
    for status in ('1', '0', '-1'):
        amount.append(len(Record.query.filter_by(status=status).all()))

    data = {
        'amount': amount,
        'status': ['Success',  'Failed', 'Abort']
    }

    bar = Bar(data, values='amount', label='status', title="Total deployment status", agg="mean", plot_width=400)
    #output_file("./depsys/templates/dash_index.html")
    #show(bar)
    script,div = components(bar)
    return render_template('dash_index.html', script=script, div=div, projects=projects)
