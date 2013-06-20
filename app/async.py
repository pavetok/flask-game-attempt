# -*- coding:utf-8 -*-
from app.models import queue
import gevent

def execute_tasks():
    while not queue.empty():
        task = queue.get()
        subj = task[0]
        operation = task[1]
        obj = task[2]
        subj.do_operation(operation, obj)