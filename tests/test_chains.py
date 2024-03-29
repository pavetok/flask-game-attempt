# -*- coding:utf-8 -*-
#!flask/bin/python
import unittest
from datetime import datetime
from app import app, db, models
from app.models import queue
from app.handlers import perform_operations


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
        # create chain of operations
        hit_and_eat = models.Operation(name='hit_and_eat',
                                       formulas='hit, eat')
        db.session.add(hit_and_eat)
        db.session.commit()
        # query from db
        figvan = models.Obj.query.get(1)
        troll = models.Obj.query.get(2)
        # perform operation
        queue.put([figvan, hit_and_eat, troll])
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