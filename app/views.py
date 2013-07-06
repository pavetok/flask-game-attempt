# -*- coding:utf-8 -*-
import json
from app import admin, db, app
from app.models import Category, Obj, Object_Property_Value, Property, Operation, Pattern, Knowledge, Interpretation, queue, Record
from app.handlers import perform_operations, interpret_situation
from flask import render_template, redirect, url_for, jsonify, Response
from flask.ext.admin.contrib.sqlamodel import ModelView

admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Obj, db.session))
admin.add_view(ModelView(Property, db.session))
admin.add_view(ModelView(Object_Property_Value, db.session))
admin.add_view(ModelView(Interpretation, db.session))
admin.add_view(ModelView(Operation, db.session))
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
    interpret_situation()
    perform_operations()
    return 'Success'

@app.route('/game')
def game():
    return render_template('layer.html')

@app.route('/update')
def update():
    # objects = []
    objects = {}
    for o in Obj.query.all():
        # obj = {"obj":
        #     {o.name: {opv.property.name: o.gp(opv.property.name) for opv in o.properties}}
        # }
        obj = {o.name: {opv.property.name: o.gp(opv.property.name) for opv in o.properties}}
        # objects.append(obj)
        objects.update(obj)
    return Response(json.dumps(objects),  mimetype='application/json')
