# -*- coding:utf-8 -*-
from hashlib import md5
from app import db


object_category = db.Table('object_category',
                       db.Column('obj_id', db.Integer,
                                 db.ForeignKey('obj.id')),
                       db.Column('category_id', db.Integer,
                                 db.ForeignKey('category.id')))


object_property = db.Table('object_property',
                           db.Column('owner_id', db.Integer,
                                     db.ForeignKey('obj.id')),
                           db.Column('property_id', db.Integer,
                                     db.ForeignKey('property.id')),
                           db.Column('target_id', db.Integer,
                                     db.ForeignKey('obj.id')))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<Category %r>' % (self.name)


class Obj(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    categories = db.relationship('Category',
                              secondary=object_category,
                              primaryjoin=(object_category.c.obj_id==id),
                              secondaryjoin=(object_category.c.category_id==id),
                              backref=db.backref('objects', lazy='dynamic'),
                              lazy='dynamic',
                              viewonly=True)
    properties = db.relationship('Property',
                              secondary = object_property,
                              primaryjoin = (object_property.c.owner_id==id),
                              secondaryjoin = (object_property.c.property_id==id),
                              backref = db.backref('objects', lazy='dynamic'),
                              lazy='dynamic',
                              viewonly=True)

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

    def add_property(self, prop):
        if not self.is_property(prop):
            self.properties.append(prop)
            return self

    def del_property(self, prop):
        if not self.is_property(prop):
            self.properties.remove(prop)
            return self

    def is_property(self, prop):
        return self.properties.filter(object_property.c.property_id == prop.id).count() > 0

    def __repr__(self):
        return '<Object %r>' % (self.name)


active_properties = db.Table('relations',
                    db.Column('active_property_id', db.Integer,
                              db.ForeignKey('property.id')),
                    db.Column('passive_property_id', db.Integer,
                              db.ForeignKey('property.id')))


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    passive_properties = db.relationship('Property',
                               secondary=active_properties,
                               primaryjoin=(active_properties.c.active_property_id==id),
                               secondaryjoin=(active_properties.c.passive_property_id==id),
                               backref=db.backref('active_properties', lazy='dynamic'),
                               lazy='dynamic')

    def add_passive(self, prop):
        if not self.is_relation(prop):
            self.passive_properties.append(prop)
            return self

    def del_relation(self, prop):
        if self.is_relation(prop):
            self.passive_properties.remove(prop)
            return self

    def is_relation(self, prop):
        return self.passive_properties.filter(active_properties.c.passive_property_id == prop.id).count() > 0

    def __repr__(self):
        return '<Property %r>' % (self.name)