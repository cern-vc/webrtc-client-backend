import os
from flask.ext.testing import TestCase
from app import create_app, db

_basedir = os.path.abspath(os.path.dirname(__file__))


class ModelTestCase(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'test_app.db')
    TESTING = True

    def create_app(self):
        # pass in test configuration
        return create_app(self)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
