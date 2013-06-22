# -*- coding:utf-8 -*-
#!flask/bin/python
import unittest
from datetime import datetime
from app import app, db, models
from app.models import queue
from app.tasks import execute_operations_tasks


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

    def test_operations_with_args(self):
        # create objects
        figvan = models.Obj(name='figvan')
        # set properties
        figvan.set_property(x=1, y=1)
        db.session.add(figvan)
        db.session.commit()
        # create operations
        move = models.Operation(name='move',
                                formulas=[
                                    'subj.x = subj.x + step.x',
                                    'subj.y = subj.y + step.y'
                                ])
        db.session.add(move)
        db.session.commit()
        # query from db
        figvan = models.Obj.query.get(1)
        kwargs = {'step.x': 1, 'step.y': 1}
        # perform operation
        # figvan.do_operation(move, **kwargs)
        queue.put([figvan, move, None, kwargs])
        execute_operations_tasks()
        # query from db
        figvan = models.Obj.query.get(1)
        # assert
        assert figvan.x == 2
        assert figvan.y == 2


if __name__ == '__main__':
    unittest.main()