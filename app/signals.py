# -*- coding:utf-8 -*-
from blinker import Namespace

operations_signals = Namespace()
operation_performed = operations_signals.signal('operation-performed')

signal_list = []
def store_signal_data(sender, operation=None, obj=None, **extra):
    try:
        data = [sender.name, operation.name, obj.name]
    except AttributeError:
        data = [sender.name, operation.name]
    signal_list.append(data)
    # print signal_list