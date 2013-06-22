# -*- coding:utf-8 -*-
import json
import logging
import time
from app import db, celery
from app.decorators import async
from app.models import Obj
import Queue
from app.models import queue
from app.signals import operation_performed
#from gevent import monkey; monkey.patch_all()
from celery.schedules import crontab


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
                    except (AttributeError):
                        pass

# logging.basicConfig(level = logging.DEBUG)

@celery.task(ignore_result=True, run_every=crontab(hour=0, minute=0))
def execute_operations_tasks():
    while not queue.empty():
        task = queue.get()
        print task
        subj = task[0]
        print subj.health
        operation = task[1]
        obj = task[2]
        subj.do_operation(operation, obj)
        # Посылаем сигнал
        operation_performed.send(subj, operation=operation, obj=obj)

execute_operations_tasks.delay()

# def execute_operations_tasks():
#     while True:
#         try:
#             task = queue.get(timeout=1)
#             print task
#             subj = task[0]
#             operation = task[1]
#             obj = task[2]
#             subj.do_operation(operation, obj)
#             # Посылаем сигнал
#             operation_performed.send(subj, operation=operation, obj=obj)
#         except Queue.Empty:
#             print 'fin'
#             return None

# gl = gevent.Greenlet(execute_operations_tasks)