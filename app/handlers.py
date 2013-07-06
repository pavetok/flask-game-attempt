# -*- coding:utf-8 -*-
import json
import time
from app.decorators import async
from app.models import Obj
from app.models import queue
#from gevent import monkey; monkey.patch_all()

@async
def start_game():
    while True:
        interpret_situation()
        perform_operations()
        time.sleep(1)

def interpret_situation():
    objects = Obj.query.all()
    for subj in objects:
        for obj in objects:
            if subj is not obj:
                for pattern in subj.patterns:
                    cons = pattern.interpretation.conditions.replace('{', '[').replace('}', ']')
                    conditions = json.loads(cons)
                    results = []
                    for con in conditions:
                        result = subj.calculate(con, obj)
                        results.append(result)
                    if all(results):
                        operation = pattern.operation
                        queue.put([subj, operation, obj])


def perform_operations():
    while not queue.empty():
        # забираем таск из очереди
        task = queue.get()
        subj = task[0]
        operation = task[1]
        obj = None
        kwargs = {}
        try:
            obj = task[2]
            kwargs = task[3]
        except IndexError:
            pass
        prev_subj = []
        # если объект только что делал шаг
        if subj in prev_subj:
            print subj
            print prev_subj
            # текущую операцию отправляем в конец очереди
            queue.put([subj, operation, obj])
        # если объект еще не делал шаг
        else:
            # выполняем операцию
            subj.do_operation(operation, obj, **kwargs)
            del prev_subj[:]
            prev_subj.append(subj)