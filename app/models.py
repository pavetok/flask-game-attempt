# -*- coding:utf-8 -*-
from hashlib import md5
from app import db
import json, re
from app.signals import operation_performed, signal_list


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

    def __unicode__(self):
        return self.name


class Obj(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    properties = db.relationship('Object_Property', backref='obj')
    patterns = db.relationship('Pattern',
                                primaryjoin="Pattern.obj_id==Obj.id",
                                backref='obj')
    records = db.relationship('Record',
                                primaryjoin="Record.obj_id==Obj.id",
                                backref='obj')

    def __getattr__(self, name):
        return Object_Property.query.join(Property,
            (Property.id==Object_Property.property_id)) \
            .filter(Property.name==name) \
            .filter(self.id==Object_Property.obj_id).first().value

    def get_property(self, prop_name):
        return Object_Property.query.join(Property,
                (Property.id==Object_Property.property_id)) \
                .filter(Property.name==prop_name) \
                .filter(self.id==Object_Property.obj_id).first().value

    gp = get_property

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

    def calculate(subj, expr, obj=None, **kwargs):
        for key in kwargs:
            expr = expr.replace(key, str(kwargs[key]))
        return eval(expr)

    def do_operation(subj, operation, obj=None, **kwargs):
        # Если операция является цепочкой операций
        if '=' not in operation.expressions:
            operations = operation.expressions.split(',')
            # Рекурсивно запускаем эту же операцию.
            for op_name in operations:
                op = Operation.query.filter(Operation.name==op_name.strip()).first()
                subj.do_operation(op, obj, **kwargs)
        else:
            exprs = operation.expressions.replace('{', '[').replace('}', ']')
            expressions = json.loads(exprs)
            for expr in expressions:
                # Вычисляем новое значение
                left_part = expr.split('=')[0].strip()
                right_part = expr.split('=')[1].strip()
                new_value =  subj.calculate(right_part, obj, **kwargs)
                # Изменяем значение свойства
                prop_type = left_part.split(".")[0]
                prop_name = left_part.split(".")[1]
                prop = {prop_name: new_value}
                if prop_type == 'subj':
                    subj.set_property(**prop)
                else:
                    obj.set_property(**prop)
        # Посылаем сигнал
        operation_performed.send(subj, operation=operation, obj=obj)

    def check_signals(subj):
        cons = subj.patterns[0].conditions.replace('{', '[').replace('}', ']')
        conditions = json.loads(cons)
        subj_signals = []
        results = []
        for signal in signal_list:
            for condition in conditions:
                result = subj.calculate(condition, signal[0])
                results.append(result)
                if result:
                    subj_signals.append(signal)
        if subj_signals != [] and all(results):
            operation = subj.patterns[0].operation
            subj.do_operation(operation)

    def __repr__(self):
        return '<Object %r>' % self.name

    def __unicode__(self):
        return self.name


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<Property %r>' % self.name

    def __unicode__(self):
        return self.name


class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    expressions = db.Column(db.Text, unique=True)
    patterns = db.relationship('Pattern',
                                primaryjoin="Pattern.operation_id==Operation.id",
                                backref='operation')

    def __repr__(self):
        return '<Operation %r>' % self.name

    def __unicode__(self):
        return self.name


class Condition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    expressions = db.Column(db.Text, unique=True)
    patterns = db.relationship('Pattern',
                                primaryjoin="Pattern.condition_id==Condition.id",
                                backref='condition')

    def __repr__(self):
        return '<Condition %r>' % self.name

    def __unicode__(self):
        return self.name


class Pattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    obj_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    operation_id = db.Column(db.Integer, db.ForeignKey('operation.id'))
    condition_id = db.Column(db.Integer, db.ForeignKey('condition.id'))

    def __repr__(self):
        return '<Pattern %r>' % self.name

    def __unicode__(self):
        return self.name


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    obj_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    body = db.Column(db.Text)

    def __repr__(self):
        return '<Record %r>' % self.body

    def __unicode__(self):
        return self.body


class Knowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    obj_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    operation_id = db.Column(db.Integer, db.ForeignKey('operation.id'))
    pattern_id = db.Column(db.Integer, db.ForeignKey('pattern.id'))

    subject = db.relationship('Obj', primaryjoin="Obj.id==Knowledge.subject_id")
    category = db.relationship('Category', primaryjoin="Category.id==Knowledge.category_id")
    obj = db.relationship('Obj', primaryjoin="Obj.id==Knowledge.obj_id")
    property = db.relationship('Property', primaryjoin="Property.id==Knowledge.property_id")
    operation = db.relationship('Operation', primaryjoin="Operation.id==Knowledge.operation_id")
    pattern = db.relationship('Pattern', primaryjoin="Pattern.id==Knowledge.pattern_id")