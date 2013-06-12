# -*- coding:utf-8 -*-
#!flask/bin/python
import unittest
from datetime import datetime
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

    def test_chain_of_operations(self):
        # create objects
        figvan = models.Obj(name='figvan')
        troll = models.Obj(name='troll')
        # set properties
        figvan.set_property(energy=2)
        figvan.set_property(angry=1)
        figvan.set_property(health=5)
        figvan.set_property(power=5)
        db.session.add(figvan)
        db.session.commit()
        troll.set_property(health=20)
        db.session.add(troll)
        db.session.commit()
        # create operations
        hit = models.Operation(name='hit',
                               formulas=[
                                   ['obj.health', '=',
                                    ['obj.health', '-',
                                     ['subj.energy', '*', 'subj.power']]],
                                   ['subj.energy', '=',
                                    ['subj.energy', '-', '1']],
                               ])
        eat = models.Operation(name='eat',
                               formulas=[
                                   ['subj.health', '=',
                                    ['subj.health', '+',
                                     ['subj.power', '*', 'subj.angry']]],
                                   ['obj.health', '=',
                                    ['obj.health', '-',
                                     ['subj.power', '*', 'subj.angry']]],
                               ])
        db.session.add(hit)
        db.session.add(eat)
        db.session.commit()
        # create chain of operations
        hit_and_eat = models.Operation(name='hit_and_eat',
                                       formulas=['chain', 'hit', 'eat'])
        db.session.add(hit_and_eat)
        db.session.commit()
        # query from db
        figvan = models.Obj.query.get(1)
        troll = models.Obj.query.get(2)
        # perform operation
        figvan.perform_operation(hit_and_eat, troll)
        db.session.add(figvan)
        db.session.add(troll)
        db.session.commit()
        # query from db
        figvan = models.Obj.query.get(1)
        troll = models.Obj.query.get(2)
        # assert
        assert figvan.get_property('health') == 10
        assert figvan.get_property('energy') == 1
        assert troll.get_property('health') == 5


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