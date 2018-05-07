#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys.models import Record


def dashboard_index():
    amount = []
    for status in ('1', '0', '-1'):
        amount.append(len(Record.query.filter_by(status=status).all()))

    data = {
        'amount': amount,
        'status': ['Success',  'Failed', 'Abort']
    }

    return data
