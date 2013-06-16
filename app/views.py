# -*- coding:utf-8 -*-
from app import admin, db
from app.models import Category, Obj, Object_Property, Property, Operation, Reaction, Knowledge
from flask.ext.admin.contrib.sqlamodel import ModelView


admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Obj, db.session))
admin.add_view(ModelView(Object_Property, db.session))
admin.add_view(ModelView(Property, db.session))
admin.add_view(ModelView(Operation, db.session))
admin.add_view(ModelView(Reaction, db.session))
admin.add_view(ModelView(Knowledge, db.session))