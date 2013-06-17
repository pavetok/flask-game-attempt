# -*- coding:utf-8 -*-
from app import admin, db, app
from app.models import Category, Obj, Object_Property, Property, Operation, Reaction, Knowledge
from flask import render_template
from flask.ext.admin.contrib.sqlamodel import ModelView


admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Obj, db.session))
admin.add_view(ModelView(Object_Property, db.session))
admin.add_view(ModelView(Property, db.session))
admin.add_view(ModelView(Operation, db.session))
admin.add_view(ModelView(Reaction, db.session))
admin.add_view(ModelView(Knowledge, db.session))


@app.route('/<name>')
def history(name):
    obj = Obj.query.filter(Obj.name==name).first()
    records = obj.records
    return render_template('history.html',
                           records = records)