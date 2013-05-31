# -*- coding:utf-8 -*-
from hashlib import md5
from app import db


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<Type %r>' % (self.name)


class Object(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<Object %r>' % (self.name)


objects_types = db.Table('objects_types',
                     db.Column('type', db.Integer,
                               db.ForeignKey('type.id')),
                     db.Column('object', db.Integer,
                               db.ForeignKey('object.id')))


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<Property %r>' % (self.name)


objects_properties = db.Table('objects_properties',
                         db.Column('owner', db.Integer,
                                   db.ForeignKey('object.id')),
                         db.Column('property', db.Integer,
                                   db.ForeignKey('property.id')),
                         db.Column('relates_to', db.Integer,
                                   db.ForeignKey('object.id')))


class Relationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    timestamp = db.Column(db.DateTime)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))

    def __repr__(self):
        return '<Relationship %r>' % (self.name)