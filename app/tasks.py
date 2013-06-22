# -*- coding:utf-8 -*-
import json
import time
from app import db
from app.decorators import async
from app.models import Obj
from app.models import queue
from app.signals import operation_performed
#from gevent import monkey; monkey.patch_all()

@async
def start_monitoring():
    while True:
        time.sleep(1)
        subjects = Obj.query.all()
        for subj in subjects:
            for pattern in subj.patterns:
                conditions = json.loads(pattern.event.conditions)
                for con in conditions:
                    try:
                        result = subj.calculate(con)
                        if result:
                            operation = pattern.operation
                            subj.do_operation(operation)
                            db.session.add(subj)
                            db.session.commit()
                    except AttributeError:
                        pass

def execute_operations_tasks():
    while not queue.empty():
        task = queue.get()
        # print task
        subj = task[0]
        operation = task[1]
        obj = None
        kwargs = {}
        try:
            obj = task[2]
            kwargs = task[3]
        except IndexError:
            pass
        # выполняем операцию
        subj.do_operation(operation, obj, **kwargs)