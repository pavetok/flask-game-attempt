# -*- coding:utf-8 -*-
#!flask/bin/python
import unittest
from time import sleep
from datetime import datetime
from app import app, db, models
from app.handlers import perform_operations
from app.models import queue


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

    def test_operations(self):
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
                                   'obj.health = obj.health - (subj.energy * subj.power)',
                                   'subj.energy = subj.energy - 1'
                               ])
        eat = models.Operation(name='eat',
                               formulas=[
                                   'subj.health = subj.health + (subj.power * subj.angry)',
                                   'obj.health = obj.health - (subj.power * subj.angry)'
                               ])
        db.session.add(hit)
        db.session.add(eat)
        db.session.commit()
        # query from db
        figvan = models.Obj.query.get(1)
        troll = models.Obj.query.get(2)
        # assert
        assert figvan.energy == 2
        assert figvan.angry == 1
        assert figvan.health == 5
        assert figvan.power == 5
        assert troll.health == 20
        # create queue
        queue.put([figvan, hit, troll])
        queue.put([figvan, eat, troll])
        perform_operations()
        # query from db
        figvan = models.Obj.query.get(1)
        troll = models.Obj.query.get(2)
        # assert
        assert figvan.health == 10
        assert figvan.energy == 1
        assert troll.health == 5


if __name__ == '__main__':
    unittest.main()