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

    def test_relationship(self):
        # create properties
        p1 = models.Property(name='Gladit')
        p2 = models.Property(name='Gladitsya')
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()
        assert p1.del_relation(p2) == None
        # create a relationship
        p1 = models.Property.query.get(1)
        p2 = models.Property.query.get(2)
        p11 = p1.add_passive(p2)
        db.session.add(p11)
        db.session.commit()
        assert p1.add_passive(p2) == None
        print p1.passive_properties.first().name
        assert p1.passive_properties.first().name == 'Gladitsya'
        assert p2.active_properties.first().name == 'Gladit'

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