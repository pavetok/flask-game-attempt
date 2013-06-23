# -*- coding:utf-8 -*-
#!flask/bin/python
import unittest
from datetime import datetime
from app import app, db, models
from app.models import queue
from app.tasks import execute_operations_tasks
from app.signals import clear_event_list


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
        # чистим список событий, иначе будут мешать события из других тестов
        clear_event_list()
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
                                formulas=[
                                    "subj.x = subj.x + subj.gp('шаг')",
                                    "subj.y = subj.y + subj.gp('шаг')"
                               ])
        db.session.add(move)
        db.session.commit()
        # create events
        obj_nearly = models.Interpretation(name="obj_nearly",
                                  conditions=[
                                    "abs(subj.x - obj.x) <= 1",
                                    "abs(subj.y - obj.y) <= 1"
                                    ])
        db.session.add(obj_nearly)
        db.session.commit()
        # create patterns
        escape = models.Pattern(name='escape',
                                 obj=troll,
                                 operation=move,
                                 event=obj_nearly)
        db.session.add(escape)
        db.session.commit()
        # query from db
        figvan = models.Obj.query.get(1)
        # perform operation
        queue.put([figvan, move])
        execute_operations_tasks()
        troll.check_events()
        execute_operations_tasks()
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
                                formulas=[
                                    "subj.x = subj.x + subj.gp('шаг')"
                                    ])
        db.session.add(move)
        db.session.commit()
        # create events
        obj_nearly = models.Interpretation(name="obj_nearly",
                                      conditions=[
                                          "abs(subj.x - obj.x) <= 1",
                                          "abs(subj.y - obj.y) <= 1"
                                      ])
        db.session.add(obj_nearly)
        db.session.commit()
        # create patterns
        escape = models.Pattern(name='escape',
                                obj=troll,
                                operation=move,
                                event=obj_nearly)
        db.session.add(escape)
        db.session.commit()
        # query from db
        figvan = models.Obj.query.get(1)
        # perform operation
        queue.put([figvan, move])
        execute_operations_tasks()
        troll.check_events()
        execute_operations_tasks()
        # query from db
        figvan = models.Obj.query.get(1)
        troll = models.Obj.query.get(2)
        # assert
        assert figvan.x == 2
        assert figvan.y == 1
        assert troll.x == 3
        assert troll.y == 3


if __name__ == '__main__':
    unittest.main()