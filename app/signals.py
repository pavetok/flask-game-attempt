# -*- coding:utf-8 -*-
from blinker import Namespace

operations_signals = Namespace()
operation_performed = operations_signals.signal('operation-performed')

signal_list = []
def store_signal_data(subj, operation=None, obj=None, **extra):
    data = [subj, operation, obj]
    signal_list.append(data)
    # print signal_list