# -*- coding:utf-8 -*-
from blinker import Namespace

signals = Namespace()
operation_performed = signals.signal('operation-performed')

event_list = []

def handle_operation_data(subj, operation=None, obj=None, **extra):
    event = [subj, operation, obj]
    event_list.append(event)
    # print event_list

def clear_event_list():
    del event_list[:]

# subscriptions
operation_performed.connect(handle_operation_data)