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

    def test_object_category(self):
        # create a category
        c1 = models.Category(name='Heroes')
        db.session.add(c1)
        db.session.commit()
        # create a obj
        o1 = models.Obj(name='Figvan')
        db.session.add(o1)
        db.session.commit()
        # add category
        c1 = models.Category.query.get(1)
        c11 = o1.add_category(c1)
        db.session.add(c11)
        db.session.commit()
        # assertions
        print o1.categories
        assert o1.categories.count() == 1
        assert o1.categories.count() == 'Heroes'
        assert c1.properties.first().name == 'Figvan'

    def test_category_property(self):
        # create a category
        c1 = models.Category(name='Heroes')
        db.session.add(c1)
        db.session.commit()
        # create an association instance
        cp1 = models.Category_Property()
        # create property
        p1 = models.Property(name='Speak')
        db.session.add(p1)
        db.session.commit()
        # add property to association instance
        cp1.property = p1
        # append association instance to category
        c1.properties.append(cp1)
        db.session.add(c1)
        db.session.commit()
        # assertions
        assert c1.properties[0].property.name == 'Speak'
        assert p1.categories[0].category.name == 'Heroes'

    def test_operation(self):
        # create properties
        p1 = models.Property(name='Speak')
        p2 = models.Property(name='Read')
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()
        # create a relation instance
        op1 = models.Operation(name='Speak-Read')
        # add properties to relation
        op1.active_property = p1
        op1.passive_property = p2
        db.session.add(op1)
        db.session.commit()
        # assertions
        assert op1.active_property.name == 'Speak'
        assert op1.passive_property.name == 'Read'

    def test_knowledge(self):
        # create instances
        o1 = models.Obj(name='Figvan')
        o2 = models.Obj(name='Food')
        p1 = models.Property(name='Edible')
        db.session.add(o1)
        db.session.add(o2)
        db.session.add(p1)
        db.session.commit()
        # create a knowledge instance
        kn1 = models.Knowledge()
        # add properties to relation
        kn1.subject = o1
        kn1.object = o2
        kn1.property = p1
        db.session.add(kn1)
        db.session.commit()
        # assertions
        assert kn1.subject.name == 'Figvan'
        assert kn1.object.name == 'Food'
        assert kn1.property.name == 'Edible'

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