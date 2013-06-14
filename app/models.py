# -*- coding:utf-8 -*-
from hashlib import md5
from app import db
import json
from app.signals import operation_performed, store_signal_data, signal_list


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
    reactions = db.relationship('Reaction',
                                primaryjoin="Reaction.obj_id==Obj.id",
                                backref='obj')

    def get_property(self, prop_name):
        return Object_Property.query.join(Property,
                (Property.id==Object_Property.property_id)) \
                .filter(Property.name==prop_name) \
                .filter(self.id==Object_Property.obj_id).first().value

    def set_property(self, **kwargs):
        for key in kwargs:
            op = self.get_obj_prop_instance(key)
            p = Property.query.filter(Property.name==key).first()
            new_value = kwargs[key]
            if op is not None:
                op.value = new_value
            elif p is not None:
                op = Object_Property(property=p, value=new_value)
                self.properties.append(op)
            else:
                p = Property(name=key)
                op = Object_Property(property=p, value=new_value)
                self.properties.append(op)

    def get_obj_prop_instance(self, prop_name):
        return Object_Property.query.join(Property,
            (Property.id==Object_Property.property_id))\
            .filter(Property.name==prop_name)\
            .filter(self.id==Object_Property.obj_id).first()

    def calculate(subj, expression, obj, **kwargs):
        prepared_expr = ''
        for arg in expression:
            if type(arg) is list:
                prepared_expr += str(subj.calculate(arg, obj, **kwargs))
            elif arg.split(".")[0] == 'subj':
                name = arg.split(".")[1]
                prepared_expr += str(subj.get_property(name))
            elif arg.split(".")[0] == 'obj':
                name = arg.split(".")[1]
                prepared_expr += str(obj.get_property(name))
            else:
                try:
                    prepared_expr += str(kwargs[arg])
                except (KeyError):
                    prepared_expr += str(arg)
        print prepared_expr
        value = eval(prepared_expr)
        # print value
        return value

    def check_signals(subj):
        conditions = json.loads(subj.reactions[0].conditions)
        subj_signals = []
        results = []
        for signal in signal_list:
            for condition in conditions:
                result = subj.calculate(condition, signal[0])
                results.append(result)
                if result:
                    subj_signals.append(signal)
        if subj_signals != [] and all(results):
            operation = subj.reactions[0].operation
            kwargs = {'step.x': 1, 'step.y': 1}
            subj.perform_operation(operation, **kwargs)

    def perform_operation(subj, operation, obj=None, **kwargs):
        # import pdb; pdb.set_trace()
        formulas = json.loads(operation.formulas)
        # Если операция является цепочкой операций
        if 'chain' in formulas:
            # Удаляем признак 'chain'
            formulas.remove('chain')
            # Для каждого из оставшихся елементов
            # рекурсивно запускаем эту же операцию.
            for op in formulas:
                op = Operation.query.filter(Operation.name==op).first()
                subj.perform_operation(op, obj, **kwargs)
        else:
            for formula in formulas:
                # Вычисляем новое значение
                new_value = subj.calculate(formula[2], obj, **kwargs)
                # Изменяем значение свойства
                prop_type = formula[0].split(".")[0]
                prop_name = formula[0].split(".")[1]
                pair = {prop_name: new_value}
                if prop_type == 'subj':
                    subj.set_property(**pair)
                else:
                    obj.set_property(**pair)
        # Посылаем сигнал
        operation_performed.send(subj, operation=operation, obj=obj)

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
    formulas = db.Column(db.String(255))
    reactions = db.relationship('Reaction',
                                primaryjoin="Reaction.operation_id==Operation.id",
                                backref='operation')

    def __init__(self, name, formulas):
        self.name = name
        self.formulas = json.dumps(formulas)

    def __repr__(self):
        return '<Operation %r>' % self.name


class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    obj_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    operation_id = db.Column(db.Integer, db.ForeignKey('operation.id'))
    conditions = db.Column(db.String(255))

    def __init__(self, name, obj, operation, conditions):
        self.name = name
        self.obj = obj
        self.operation = operation
        self.conditions = json.dumps(conditions)

    def __repr__(self):
        return '<Reaction %r>' % self.name


class Knowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    obj_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    operation_id = db.Column(db.Integer, db.ForeignKey('operation.id'))

    subjects = db.relationship('Obj', primaryjoin="Obj.id==Knowledge.subject_id")
    categories = db.relationship('Category', primaryjoin="Category.id==Knowledge.category_id")
    objects = db.relationship('Obj', primaryjoin="Obj.id==Knowledge.obj_id")
    properties = db.relationship('Property', primaryjoin="Property.id==Knowledge.property_id")
    operations = db.relationship('Operation', primaryjoin="Operation.id==Knowledge.operation_id")


# subscriptions
operation_performed.connect(store_signal_data)