import os
from unittest import TestCase

from app.app_factory import create_app

_basedir = os.path.abspath(os.path.dirname(__file__))


class CreateAppTest(TestCase):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'test_app.db')
    TESTING = True
    ENABLE_SSO = False
    WTF_CSRF_ENABLED = False
    WTF_CSRF_SECRET_KEY = "somethingimpossibletoguess"
    SECRET_KEY = 'This string will be replaced with a proper key in production.'
    TOKEN_EXPIRATION_SECONDS = 600
    BASE_CERN_OAUTH2_API_URL = "https://oauthresource.web.cern.ch"
    SENTRY_ENABLED = False
    SENTRY_DSN = "<ADD SENTRY DSN STRING>"

    def test_sentry_conditions(self):
        try:
            self.SENTRY_ENABLED = True
            self.SENTRY_DSN = None

            create_app(self)
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)




