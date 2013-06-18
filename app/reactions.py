# -*- coding:utf-8 -*-
import json
from app import db
from app.models import Obj


def start_monitoring():
    subjects = Obj.query.all()
    for subj in subjects:
        for reaction in subj.reactions:
            conditions = json.loads(reaction.conditions)
            for con in conditions:
                try:
                    result = subj.calculate(con)
                    print result
                    if result:
                        operation = reaction.operation
                        # print operation
                        subj.do_operation(operation)
                        db.session.add(subj)
                        db.session.commit()
                except (AttributeError):
                    pass

start_monitoring()