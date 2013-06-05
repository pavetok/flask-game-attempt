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

    def test_category_object(self):
        # create a category
        c1 = models.Category(name='Heroes')
        c2 = models.Category(name='Animals')
        db.session.add(c1)
        db.session.add(c2)
        db.session.commit()
        # create a object
        o1 = models.Obj(name='Locky')
        o2 = models.Obj(name='Cat')
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
        assert o1.categories.first().name == 'Heroes'
        assert c1.objects.first().name == 'Locky'
        assert o2.categories.first().name == 'Animals'
        assert c2.objects.first().name == 'Cat'

    def test_category_property(self):
        # create a category
        c1 = models.Category(name='Heroes')
        c2 = models.Category(name='Animals')
        db.session.add(c1)
        db.session.add(c2)
        db.session.commit()
        # create a property
        p1 = models.Property(name='Speak')
        p2 = models.Property(name='Shhhh')
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()
        # query instances
        c1 = models.Category.query.get(1)
        c2 = models.Category.query.get(2)
        p1 = models.Property.query.get(1)
        p2 = models.Property.query.get(2)
        # append
        p1.categories.append(c1)
        c2.properties.append(p2)
        db.session.add(p1)
        db.session.add(c2)
        db.session.commit()
        # query instances
        c1 = models.Category.query.get(1)
        c2 = models.Category.query.get(2)
        p1 = models.Property.query.get(1)
        p2 = models.Property.query.get(2)
        # assertions
        assert p1.categories.first().name == 'Heroes'
        assert c1.properties.first().name == 'Speak'
        assert p2.categories.first().name == 'Animals'
        assert c2.properties.first().name == 'Shhhh'

    def test_relaction(self):
        # create qualities
        q1 = models.Quality(name='Consuming', is_active=True)
        q2 = models.Quality(name='Eaten', is_active=False)
        db.session.add(q1)
        db.session.add(q2)
        db.session.commit()
        # create a relaction and add qualities
        r1 = models.Relaction(name='Eat', active_quality=q1, passive_quality=q2)
        # r1.active_quality = q1
        # r1.passive_quality = q2
        db.session.add(r1)
        db.session.commit()
        # query instance
        r1 = models.Relaction.query.get(1)
        # assertions
        assert r1.name == 'Eat'
        assert r1.active_quality.name == 'Consuming'
        assert r1.passive_quality.name == 'Eaten'

    def test_knowledge(self):
        # create instances
        o1 = models.Obj(name='Figvan')
        o2 = models.Obj(name='Food')
        db.session.add(o1)
        db.session.add(o2)
        db.session.commit()
        # create a knowledge instance
        kn1 = models.Knowledge()
        # query instances
        o1 = models.Obj.query.get(1)
        o2 = models.Obj.query.get(2)
        # add properties to relation
        kn1.subject = o1
        kn1.obj = o2
        db.session.add(kn1)
        db.session.commit()
        # query instance
        kn1 = models.Knowledge.query.get(1)
        # assertions
        assert kn1.subject.name == 'Figvan'
        assert kn1.obj.name == 'Food'

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