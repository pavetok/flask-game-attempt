# -*- coding:utf-8 -*-
from Queue import Queue
from hashlib import md5
from app import db
import json
from app.signals import operation_performed, event_list
from sqlalchemy.exc import InvalidRequestError

queue = Queue()

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

class Value(db.Model):
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
    properties = db.relationship('Value', backref='obj')
    patterns = db.relationship('Pattern',
                                primaryjoin="Pattern.obj_id==Obj.id",
                                backref='subj')
    records = db.relationship('Record',
                                primaryjoin="Record.obj_id==Obj.id",
                                backref='obj')

    def __getattr__(self, name):
        return Value.query.join(Property,
            (Property.id==Value.property_id)) \
            .filter(Property.name==name) \
            .filter(self.id==Value.obj_id).first().value

    def get_property(self, prop_name):
        return Value.query.join(Property,
                (Property.id==Value.property_id)) \
                .filter(Property.name==prop_name) \
                .filter(self.id==Value.obj_id).first().value

    gp = get_property

    def set_property(self, **kwargs):
        for key in kwargs:
            op = self.get_obj_prop_instance(key)
            p = Property.query.filter(Property.name==key).first()
            new_value = kwargs[key]
            if op is not None:
                op.value = new_value
            elif p is not None:
                op = Value(property=p, value=new_value)
                self.properties.append(op)
            else:
                p = Property(name=key)
                op = Value(property=p, value=new_value)
                self.properties.append(op)

    def get_obj_prop_instance(self, prop_name):
        return Value.query.join(Property,
            (Property.id==Value.property_id))\
            .filter(Property.name==prop_name)\
            .filter(self.id==Value.obj_id).first()

    def calculate(subj, expr, obj=None, **kwargs):
        for key in kwargs:
            expr = expr.replace(key, str(kwargs[key]))
        return eval(expr)

    def do_operation(subj, operation, obj=None, **kwargs):
        # если операция является цепочкой операций
        if '=' not in operation.formulas:
            operations = operation.formulas.split(',')
            # рекурсивно запускаем вложенные операции
            for op_name in operations:
                op = Operation.query.filter(Operation.name==op_name.strip()).first()
                queue.put([subj, op, obj, kwargs])
        # иначе, если операция является конечной
        else:
            # получаем формулы данной операции
            expressions = operation.formulas.replace('{', '[').replace('}', ']')
            formulas = json.loads(expressions)
            # вычисляем каждую из формул
            for formula in formulas:
                left_part = formula.split('=')[0].strip()
                right_part = formula.split('=')[1].strip()
                new_value =  subj.calculate(right_part, obj, **kwargs)
                prop_type = left_part.split(".")[0]
                prop_name = left_part.split(".")[1]
                prop = {prop_name: new_value}
                if prop_type == 'subj':
                    subj.set_property(**prop)
                else:
                    obj.set_property(**prop)
            # создаем и добавляем запись в историю
            try:
                record = u"%s выполнил(а) %s над %s" % (subj.name, operation.name, obj.name)
            except (AttributeError):
                record = u"%s выполнил(а) %s" % (subj.name, operation.name)
            rec = Record(body=record)
            subj.records.append(rec)
            # print subj, subj.x
            # коммитим изменения в бд
            db.session.add(subj)
            if obj != None:
                try:
                    db.session.add(obj)
                except InvalidRequestError:
                    db.session.merge(obj)
            db.session.commit()
            # print 'commited'
            # посылаем сигнал о том, что операция выполнена
            operation_performed.send(subj, operation=operation, obj=obj)

    def __repr__(self):
        return '<Object %s>' % self.name

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
    formulas = db.Column(db.Text, unique=True)
    patterns = db.relationship('Pattern',
                                primaryjoin="Pattern.operation_id==Operation.id",
                                backref='operation')

    def __repr__(self):
        return '<Operation %s>' % self.name

    def __unicode__(self):
        return self.name


class Interpretation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    conditions = db.Column(db.Text, unique=True)
    patterns = db.relationship('Pattern',
                                primaryjoin="Pattern.interpretation_id==Interpretation.id",
                                backref='interpretation')

    def __repr__(self):
        return '<Interpretation %s>' % self.name

    def __unicode__(self):
        return self.name


class Pattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    obj_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    operation_id = db.Column(db.Integer, db.ForeignKey('operation.id'))
    interpretation_id = db.Column(db.Integer, db.ForeignKey('interpretation.id'))

    def __repr__(self):
        return '<Pattern %s>' % self.name

    def __unicode__(self):
        return self.name


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    obj_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    body = db.Column(db.Text)

    def __repr__(self):
        return '<Record %s>' % self.body

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