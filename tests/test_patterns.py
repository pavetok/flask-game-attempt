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
        kwargs = {'x': 1, 'y': 1, 'шаг': 1}
        figvan.set_property(**kwargs)
        db.session.add(figvan)
        db.session.commit()
        kwargs = {'x': 3, 'y': 3, 'шаг': 1}
        troll.set_property(**kwargs)
        db.session.add(troll)
        db.session.commit()
        # create operations
        move = models.Operation(name='move',
                                expressions=[
                                    "subj.x = subj.x + subj.gp('шаг')",
                                    "subj.y = subj.y + subj.gp('шаг')"
                               ])
        db.session.add(move)
        db.session.commit()
        # create conditions
        obj_nearly = models.Condition(name="obj_nearly",
                                expressions=[
                                    "abs(subj.x - obj.x) <= 1",
                                    "abs(subj.y - obj.y) <= 1"
                                    ])
        db.session.add(obj_nearly)
        db.session.commit()
        # create patterns
        escape = models.Pattern(name='escape',
                                 obj=troll,
                                 operation=move,
                                 condition=obj_nearly)
        db.session.add(escape)
        db.session.commit()
        # query from db
        figvan = models.Obj.query.get(1)
        # perform operation
        figvan.do_operation(move)
        db.session.add(figvan)
        db.session.commit()
        # react
        troll.check_signals()
        # query from db
        figvan = models.Obj.query.get(1)
        troll = models.Obj.query.get(2)
        # assert
        assert figvan.x == 2
        assert figvan.y == 2
        assert troll.x == 4
        assert troll.y == 4

    def test_no_reaction(self):
        # create objects
        figvan = models.Obj(name='figvan')
        troll = models.Obj(name='troll')
        # set properties
        kwargs = {'x': 1, 'y': 1, 'шаг': 1}
        figvan.set_property(**kwargs)
        db.session.add(figvan)
        db.session.commit()
        kwargs = {'x': 3, 'y': 3, 'шаг': 1}
        troll.set_property(**kwargs)
        db.session.add(troll)
        db.session.commit()
        # create operations
        move = models.Operation(name='move',
                                expressions=[
                                    "subj.x = subj.x + subj.gp('шаг')"
                                    ])
        db.session.add(move)
        db.session.commit()
        # create conditions
        obj_nearly = models.Condition(name="obj_nearly",
                                      expressions=[
                                          "abs(subj.x - obj.x) <= 1",
                                          "abs(subj.y - obj.y) <= 1"
                                      ])
        db.session.add(obj_nearly)
        db.session.commit()
        # create patterns
        escape = models.Pattern(name='escape',
                                obj=troll,
                                operation=move,
                                condition=obj_nearly)
        db.session.add(escape)
        db.session.commit()
        # query from db
        figvan = models.Obj.query.get(1)
        # perform operation
        figvan.do_operation(move)
        db.session.add(figvan)
        db.session.commit()
        # react
        troll.check_signals()
        # query from db
        figvan = models.Obj.query.get(1)
        troll = models.Obj.query.get(2)
        # assert
        assert figvan.x == 2
        assert figvan.y == 1
        assert troll.x == 3
        assert troll.y == 3


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