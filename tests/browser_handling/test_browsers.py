from sqlalchemy.exc import IntegrityError, InvalidRequestError

from app.extensions import db
from app.models.browser_handling import Browser
from tests import BaseTestCase


class BrowserTest(BaseTestCase):

    def add_test_browsers(self):
        firefox = Browser(name="Firefox")
        opera = Browser(name="Opera")
        chrome = Browser(name="Chrome")
        chromium = Browser(name="Chromium")
        safari = Browser(name="Safari")

        db.session.add(firefox)
        db.session.add(opera)
        db.session.add(chrome)
        db.session.add(chromium)
        db.session.add(safari)

        db.session.commit()

    def test_add_browser(self):

        firefox = Browser(name="Firefox")
        db.session.add(firefox)
        db.session.commit()

        # this works
        assert firefox in db.session

    def test_remove_os(self):

        firefox = Browser(name="Firefox")
        db.session.add(firefox)
        db.session.commit()

        # this works
        assert firefox in db.session

        db.session.delete(firefox)
        db.session.commit()

        # this works
        assert firefox not in db.session

    def test_add_twice_browser(self):

        firefox = Browser(name="Firefox")
        db.session.add(firefox)
        db.session.commit()

        firefox2 = Browser(name="Firefox")
        db.session.add(firefox2)
        try:
            db.session.commit()
            assert None
        except IntegrityError:
            db.session.rollback()
            assert True

        firefox_found = Browser.query.filter_by(name="Firefox").one()
        # this works
        assert firefox_found in db.session

    def test_remove_unexisting_browser(self):

        firefox = Browser(name="Firefox")
        try:
            db.session.delete(firefox)
        except InvalidRequestError:
            assert True
        db.session.commit()

        # this works
        assert firefox not in db.session