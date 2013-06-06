# -*- coding:utf-8 -*-
#!flask/bin/python
import unittest
from datetime import datetime, timedelta
from app import app, db, models
from config import basedir
from coverage import coverage
import os

cov = coverage(branch = True, omit = ['venv/*', 'tests.py'])
cov.start()

class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:395885@localhost/test.db'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_operation(self):
        # create instances
        o1 = models.Obj(name='figvan')
        o2 = models.Obj(name='troll')
        p1 = models.Property(name='health')
        p2 = models.Property(name='power')
        op1 = models.Operation(name='hit', formula='(health - power)')
        db.session.add(o1)
        db.session.add(o2)
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(op1)
        db.session.commit()
        # Set properties
        o1.modify_property(power=5)
        o2.modify_property(health=10)
        assert o1.get_property('power') == 5
        assert o2.get_property('health') == 10
        # perform operation
        o1.perform_operation(operation=op1, target=o2)
        # check
        assert o2.get_property('health') == 5

    def test_category_object(self):
        # create a category
        c1 = models.Category(name='heroes')
        c2 = models.Category(name='animals')
        db.session.add(c1)
        db.session.add(c2)
        db.session.commit()
        # create a object
        o1 = models.Obj(name='locky')
        o2 = models.Obj(name='cat')
        db.session.add(o1)
        db.session.add(o2)
        db.session.commit()
        # query instances
        c1 = models.Category.query.get(1)
        c2 = models.Category.query.get(2)
        o1 = models.Obj.query.get(1)
        o2 = models.Obj.query.get(2)
        # append
        o1.categories.append(c1)
        c2.objects.append(o2)
        db.session.add(o1)
        db.session.add(c2)
        db.session.commit()
        # query instances
        c1 = models.Category.query.get(1)
        c2 = models.Category.query.get(2)
        o1 = models.Obj.query.get(1)
        o2 = models.Obj.query.get(2)
        # assertions
        assert o1.categories.first().name == 'heroes'
        assert c1.objects.first().name == 'locky'
        assert o2.categories.first().name == 'animals'
        assert c2.objects.first().name == 'cat'

    def test_object_property(self):
        # create objects
        o1 = models.Obj(name='figvan')
        o2 = models.Obj(name='troll')
        db.session.add(o1)
        db.session.add(o2)
        db.session.commit()
        # create properties
        p1 = models.Property(name='power')
        p2 = models.Property(name='health')
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()
        # query instances
        o1 = models.Obj.query.get(1)
        o2 = models.Obj.query.get(2)
        p1 = models.Property.query.get(1)
        p2 = models.Property.query.get(2)
        # create association instances
        op1 = models.Object_Property()
        op2 = models.Object_Property()
        # add properties and values to association instances
        op1.property = p1
        op1.value = 5
        op2.property = p2
        op2.value = 10
        # append association instances to objects
        o1.properties.append(op1)
        o2.properties.append(op2)
        db.session.add(o1)
        db.session.add(o2)
        db.session.commit()
        # query instances
        o1 = models.Obj.query.get(1)
        o2 = models.Obj.query.get(2)
        op1 = models.Object_Property.query.get(1)
        op2 = models.Object_Property.query.get(2)
        p1 = models.Property.query.get(1)
        p2 = models.Property.query.get(2)
        # assertions
        assert o1.properties[0].property.name == 'power'
        assert o2.properties[0].property.name == 'health'
        assert op1.value == 5
        assert op2.value == 10
        assert p1.objects[0].obj.name == 'figvan'
        assert p2.objects[0].obj.name == 'troll'


    def test_category_operation(self):
        # create a category
        c1 = models.Category(name='heroes')
        c2 = models.Category(name='animals')
        db.session.add(c1)
        db.session.add(c2)
        db.session.commit()
        # create a operations
        op1 = models.Operation(name='speak')
        op2 = models.Operation(name='walk')
        db.session.add(op1)
        db.session.add(op2)
        db.session.commit()
        # query instances
        c1 = models.Category.query.get(1)
        c2 = models.Category.query.get(2)
        op1 = models.Operation.query.get(1)
        op2 = models.Operation.query.get(2)
        # append
        op1.categories.append(c1)
        c2.operations.append(op2)
        db.session.add(op1)
        db.session.add(c2)
        db.session.commit()
        # query instances
        c1 = models.Category.query.get(1)
        c2 = models.Category.query.get(2)
        op1 = models.Operation.query.get(1)
        op2 = models.Operation.query.get(2)
        # assertions
        assert op1.categories.first().name == 'heroes'
        assert c1.operations.first().name == 'speak'
        assert op2.categories.first().name == 'animals'
        assert c2.operations.first().name == 'walk'

    def test_knowledge(self):
        # create instances
        o1 = models.Obj(name='figvan')
        c1 = models.Category(name='heroes')
        o2 = models.Obj(name='troll')
        p1 = models.Property(name='power')
        op1 = models.Operation(name='hit')
        db.session.add(o1)
        db.session.add(c1)
        db.session.add(o2)
        db.session.add(p1)
        db.session.add(op1)
        db.session.commit()
        # create a knowledge instance
        kn1 = models.Knowledge()
        # query instances
        o1 = models.Obj.query.get(1)
        c1 = models.Category.query.get(1)
        o2 = models.Obj.query.get(2)
        p1 = models.Property.query.get(1)
        op1 = models.Operation.query.get(1)
        # add properties to relation
        kn1.subject = o1
        kn1.category = c1
        kn1.obj = o2
        kn1.property = p1
        kn1.operation = op1
        db.session.add(kn1)
        db.session.commit()
        # query instance
        kn1 = models.Knowledge.query.get(1)
        # assertions
        assert kn1.subject.name == 'figvan'
        assert kn1.category.name == 'heroes'
        assert kn1.obj.name == 'troll'
        assert kn1.property.name == 'power'
        assert kn1.operation.name == 'hit'



if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print "\n\nCoverage Report:\n"
    cov.report()
    print "HTML version: " + os.path.join(basedir, "tmp/coverage/index.html")
    cov.html_report(directory = 'tmp/coverage')
    cov.erase()