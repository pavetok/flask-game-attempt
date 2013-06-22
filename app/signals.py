# -*- coding:utf-8 -*-
from blinker import Namespace

signals = Namespace()
operation_performed = signals.signal('operation-performed')

signal_list = []
def handle_operation_data(subj, operation=None, obj=None, **extra):
    signal = [subj, operation, obj]
    # print subj.health
    signal_list.append(signal)
    try:
        record = u"%s выполнил(а) %s над %s" % (subj.name, operation.name, obj.name)
    except (AttributeError):
        record = u"%s выполнил(а) %s" % (subj.name, operation.name)
    from app.models import Record
    rec = Record(body=record)
    subj.records.append(rec)
    from app import db
    db.session.add(subj)
    db.session.add(obj)
    db.session.commit()

# subscriptions
operation_performed.connect(handle_operation_data)