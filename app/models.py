# -*- coding:utf-8 -*-
from hashlib import md5
from app import db
import json


category_object = db.Table('category_object',
                          db.Column('category_id', db.Integer,
                                    db.ForeignKey('category.id')),
                          db.Column('obj_id', db.Integer,
                                    db.ForeignKey('obj.id')))


category_operation = db.Table('category_operation',
                             db.Column('category_id', db.Integer,
                                       db.ForeignKey('category.id')),
                             db.Column('operation_id', db.Integer,
                                       db.ForeignKey('operation.id')))

class Object_Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    obj_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    value = db.Column(db.Integer)
    property = db.relationship("Property", backref='objects')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    objects = db.relationship('Obj',
                              secondary=category_object,
                              backref=db.backref('categories', lazy='dynamic'),
                              lazy='dynamic')
    operations = db.relationship('Operation',
                                 secondary=category_operation,
                                 backref=db.backref('categories', lazy='dynamic'),
                                 lazy='dynamic')

    def __repr__(self):
        return '<Category %r>' % self.name


class Obj(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    properties = db.relationship('Object_Property', backref='obj')

    def set_property_value(self, **kwargs):
        for key in kwargs:
            op = self.get_obj_prop_inst(key)
            p = Property.query.filter(Property.name==key).first()
            if op is not None:
                op.value = kwargs[key]
            elif p is not None:
                op = Object_Property(property=p, value=kwargs[key])
                self.properties.append(op)
            else:
                p = Property(name=key)
                op = Object_Property(property=p, value=kwargs[key])
                self.properties.append(op)


    def get_property_value(self, prop_name):
        return Object_Property.query.join(Property,
             (Property.id==Object_Property.property_id))\
             .filter(Property.name==prop_name)\
             .filter(self.id==Object_Property.obj_id).first().value

    def get_obj_prop_inst(self, prop_name):
        return Object_Property.query.join(Property,
            (Property.id==Object_Property.property_id))\
            .filter(Property.name==prop_name)\
            .filter(self.id==Object_Property.obj_id).first()

    def calculate(subj, formula, obj):
        expr = ''
        for arg in formula:
            if type(arg) is list:
                expr += str(subj.calculate(arg, obj))
            elif arg.split(".")[0] == 'subj':
                prop_name = arg.split(".")[1]
                expr += str(subj.get_property_value(prop_name))
            elif arg.split(".")[0] == 'obj':
                prop_name = arg.split(".")[1]
                expr += str(obj.get_property_value(prop_name))
            else:
                expr += str(arg)
        value = eval(expr)
        return value

    def perform_operation(subj, operation, obj):
        formula = json.loads(operation.formula)
        # Вычисляем новое значение
        new_value = subj.calculate(formula[2], obj)
        # Изменяем значение свойства
        prop_type = formula[0].split(".")[0]
        prop_name = formula[0].split(".")[1]
        pair = {prop_name: new_value}
        if prop_type == 'subj':
            subj.set_property_value(**pair)
        else:
            obj.set_property_value(**pair)

    def add_category(self, category):
        if not self.is_category(category):
            self.categories.append(category)
            return self

    def del_category(self, category):
        if not self.is_category(category):
            self.categories.remove(category)
            return self

    def is_category(self, category):
        return self.categories.filter(category_object.c.category_id==category.id)\
                   .count() > 0

    def __repr__(self):
        return '<Object %r>' % self.name


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<Property %r>' % self.name


class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    formula = db.Column(db.String(120))

    def __init__(self, name, formula):
        self.name = name
        self.formula = json.dumps(formula)

    def __repr__(self):
        return '<Operation %r>' % self.name


class Knowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    obj_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    operation_id = db.Column(db.Integer, db.ForeignKey('operation.id'))

    subject = db.relationship('Obj', primaryjoin="Obj.id==Knowledge.subject_id")
    category = db.relationship('Category', primaryjoin="Category.id==Knowledge.category_id")
    obj = db.relationship('Obj', primaryjoin="Obj.id==Knowledge.obj_id")
    property = db.relationship('Property', primaryjoin="Property.id==Knowledge.property_id")
    operation = db.relationship('Operation', primaryjoin="Operation.id==Knowledge.operation_id")