# -*- coding:utf-8 -*-
from blinker import Namespace

operations_signals = Namespace()
operation_performed = operations_signals.signal('operation-performed')

signal_list = []
def store_signal_data(subj, operation=None, obj=None, **extra):
    signal = [subj, operation, obj]
    signal_list.append(signal)
    try:
        record = "%s выполнил операцию %s с объектом %s" % (subj.name, operation.name, obj.name)
    except (AttributeError):
        record = "%s выполнил операцию %s" % (subj.name, operation.name)
    from app.models import Record
    rec = Record(body=record)
    subj.records.append(rec)
    # print signal_list


# subscriptions
operation_performed.connect(store_signal_data)