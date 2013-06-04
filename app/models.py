# -*- coding:utf-8 -*-
from hashlib import md5
from app import db


object_category = db.Table('object_category',
                           db.Column('obj_id', db.Integer,
                                     db.ForeignKey('obj.id')),
                           db.Column('category_id', db.Integer,
                                     db.ForeignKey('category.id')))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    properties = db.relationship('Category_Property', backref='category')

    def __repr__(self):
        return '<Category %r>' % self.name


class Obj(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    categories = db.relationship('Category',
                  secondary=object_category, primaryjoin=(object_category.c.obj_id==id),
                  secondaryjoin=(object_category.c.category_id==id),
                  backref=db.backref('objects', lazy='dynamic'),
                  lazy='dynamic', viewonly=True)

    def add_category(self, category):
        if not self.is_category(category):
            self.categories.append(category)
            return self

    def del_category(self, category):
        if not self.is_category(category):
            self.categories.remove(category)
            return self

    def is_category(self, category):
        return self.categories.filter(object_category.c.category_id == category.id).count() > 0

    def __repr__(self):
        return '<Object %r>' % self.name


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<Property %r>' % self.name


class Category_Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), primary_key=True)
    property = db.relationship("Property", backref='categories')


class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    active_property_id = db.Column(db.Integer, db.ForeignKey('property.id'), primary_key=True)
    passive_property_id = db.Column(db.Integer, db.ForeignKey('property.id'), primary_key=True)
    passive_property = db.relationship('Property',
                                       primaryjoin="Property.id==Operation.passive_property_id")
    active_property = db.relationship('Property',
                                      primaryjoin="Property.id==Operation.active_property_id")

    def __repr__(self):
        return '<Operation %r>' % self.name


class Knowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('obj.id'), primary_key=True)
    object_id = db.Column(db.Integer, db.ForeignKey('obj.id'), primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), primary_key=True)
    subject = db.relationship('Obj',
                              primaryjoin="Obj.id==Knowledge.subject_id")
    object = db.relationship('Obj',
                             primaryjoin="Obj.id==Knowledge.object_id")
    property = db.relationship('Property',
                               primaryjoin="Property.id==Knowledge.property_id")