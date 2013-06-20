# -*- coding:utf-8 -*-
import json
from app import db
from app.models import Obj


def start_monitoring():
    subjects = Obj.query.all()
    for subj in subjects:
        for pattern in subj.patterns:
            conditions = json.loads(pattern.condition.expressions)
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