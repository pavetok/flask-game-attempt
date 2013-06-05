# -*- coding:utf-8 -*-
from hashlib import md5
from app import db


category_object = db.Table('category_object',
                          db.Column('category_id', db.Integer,
                                    db.ForeignKey('category.id')),
                          db.Column('obj_id', db.Integer,
                                    db.ForeignKey('obj.id')))


category_property = db.Table('category_property',
                             db.Column('category_id', db.Integer,
                                       db.ForeignKey('category.id')),
                             db.Column('property_id', db.Integer,
                                       db.ForeignKey('property.id')))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    objects = db.relationship('Obj',
                             secondary=category_object,
                             backref=db.backref('categories', lazy='dynamic'),
                             lazy='dynamic')
    properties = db.relationship('Property',
                                 secondary=category_property,
                                 backref=db.backref('categories', lazy='dynamic'),
                                 lazy='dynamic')

    def __repr__(self):
        return '<Category %r>' % self.name


class Obj(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)

    def add_category(self, category):
        if not self.is_category(category):
            self.categories.append(category)
            return self

    def del_category(self, category):
        if not self.is_category(category):
            self.categories.remove(category)
            return self

    def is_category(self, category):
        return self.categories.filter(category_object.c.category_id==category.id).count() > 0

    def __repr__(self):
        return '<Object %r>' % self.name


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<Property %r>' % self.name


class Relaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    active_quality_id = db.Column(db.Integer, db.ForeignKey('quality.id'), unique=True)
    passive_quality_id = db.Column(db.Integer, db.ForeignKey('quality.id'), unique=True)
    active_quality = db.relationship('Quality',
                                      primaryjoin="Quality.id==Relaction.active_quality_id")
    passive_quality = db.relationship('Quality',
                                      primaryjoin="Quality.id==Relaction.passive_quality_id")


class Quality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    is_active = db.Column(db.Boolean)

    def __repr__(self):
        return '<Quality %r>' % self.name


class Knowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    obj_id = db.Column(db.Integer, db.ForeignKey('obj.id'))
    subject = db.relationship('Obj',
                              primaryjoin="Obj.id==Knowledge.subject_id")
    obj = db.relationship('Obj',
                          primaryjoin="Obj.id==Knowledge.obj_id")