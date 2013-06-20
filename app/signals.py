# -*- coding:utf-8 -*-
from blinker import Namespace

operations_signals = Namespace()
operation_performed = operations_signals.signal('operation-performed')

signal_list = []
def store_signal_data(subj, operation=None, obj=None, **extra):
    signal = [subj, operation, obj]
    signal_list.append(signal)
    try:
        record = u"%s выполнил(а) %s над %s" % (subj.name, operation.name, obj.name)
    except (AttributeError):
        record = u"%s выполнил(а) %s" % (subj.name, operation.name)
    from app.models import Record
    rec = Record(body=record)
    subj.records.append(rec)

# subscriptions
operation_performed.connect(store_signal_data)