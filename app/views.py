# -*- coding:utf-8 -*-
from app import admin, db, app
from app.models import Category, Obj, Object_Property, Property, Operation, Pattern, Knowledge, Event, queue, Record
from app.tasks import execute_operations_tasks
from flask import render_template, redirect, url_for
from flask.ext.admin.contrib.sqlamodel import ModelView

admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Obj, db.session))
admin.add_view(ModelView(Object_Property, db.session))
admin.add_view(ModelView(Property, db.session))
admin.add_view(ModelView(Operation, db.session))
admin.add_view(ModelView(Event, db.session))
admin.add_view(ModelView(Pattern, db.session))
admin.add_view(ModelView(Record, db.session))
admin.add_view(ModelView(Knowledge, db.session))

@app.route('/history/<subj>')
def history(subj):
    subj = Obj.query.filter(Obj.name==subj).first()
    records = subj.records
    return render_template('history.html',
                           records = records)

@app.route('/start/<subj>/<operation>')
@app.route('/start/<subj>/<operation>/<obj>')
def start(subj, operation, obj=None):
    subj = Obj.query.filter(Obj.name==subj).first()
    op = Operation.query.filter(Operation.name==operation).first()
    if obj is not None:
        obj = Obj.query.filter(Obj.name==obj).first()
        queue.put([subj, op, obj])
    else:
        subj.do_operation(op)
        queue.put([subj, op])
    execute_operations_tasks()
    obj.check_events()
    execute_operations_tasks()
    return 'Success'