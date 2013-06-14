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

    def test_reaction(self):
        # create objects
        figvan = models.Obj(name='figvan')
        troll = models.Obj(name='troll')
        # set properties
        figvan.set_property(x=1, y=1)
        db.session.add(figvan)
        db.session.commit()
        troll.set_property(x=3, y=3)
        db.session.add(troll)
        db.session.commit()
        # create operations
        move = models.Operation(name='move',
                               formulas=[
                                   ['subj.x', '=',
                                    ['subj.x', '+', 'step.x']],
                                   ['subj.y', '=',
                                    ['subj.y', '+', 'step.y']],
                               ])
        db.session.add(move)
        db.session.commit()
        # create reactions
        escape = models.Reaction(name='escape',
                                 obj=troll,
                                 operation=move,
                                 conditions=[
                                     ['abs(', 'subj.x', '-', 'obj.x', ')', '<=', '1'],
                                     ['abs(', 'subj.y', '-', 'obj.y', ')', '<=', '1'],
                                     ])
        db.session.add(escape)
        db.session.commit()
        # query from db
        figvan = models.Obj.query.get(1)
        kwargs = {'step.x': 1, 'step.y': 1}
        # perform operation
        figvan.perform_operation(move, **kwargs)
        db.session.add(figvan)
        db.session.commit()
        # react
        troll.check_signals()
        # query from db
        figvan = models.Obj.query.get(1)
        troll = models.Obj.query.get(2)
        # assert
        assert figvan.get_property('x') == 2
        assert figvan.get_property('y') == 2
        assert troll.get_property('x') == 4
        assert troll.get_property('y') == 4

    def test_no_reaction(self):
        # create objects
        figvan = models.Obj(name='figvan')
        troll = models.Obj(name='troll')
        # set properties
        figvan.set_property(x=1, y=1)
        db.session.add(figvan)
        db.session.commit()
        troll.set_property(x=3, y=3)
        db.session.add(troll)
        db.session.commit()
        # create operations
        move = models.Operation(name='move',
                                formulas=[
                                    ['subj.x', '=',
                                     ['subj.x', '+', 'step.x']],
                                    ['subj.y', '=',
                                     ['subj.y', '+', 'step.y']],
                                    ])
        db.session.add(move)
        db.session.commit()
        # create reactions
        escape = models.Reaction(name='escape',
                                 obj=troll,
                                 operation=move,
                                 conditions=[
                                     ['1', '>=', 'abs', '(', 'subj.x', '-', 'obj.x', ')'],
                                     ['1', '>=', 'abs', '(', 'subj.y', '-', 'obj.y', ')'],
                                     ])
        db.session.add(escape)
        db.session.commit()
        # query from db
        figvan = models.Obj.query.get(1)
        kwargs = {'step.x': 1, 'step.y': 0}
        # perform operation
        figvan.perform_operation(move, **kwargs)
        db.session.add(figvan)
        db.session.commit()
        # react
        troll.check_signals()
        # query from db
        figvan = models.Obj.query.get(1)
        troll = models.Obj.query.get(2)
        # assert
        assert figvan.get_property('x') == 2
        assert figvan.get_property('y') == 1
        assert troll.get_property('x') == 3
        assert troll.get_property('y') == 3


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