from flask.ext.testing import TestCase
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from app import db

from app.browser_handling.tests import ModelTestCase
from app.browser_handling.models import Browser, BrowserFactory


class BrowserTest(ModelTestCase):

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


class OperatingSystemFactoryTest(ModelTestCase):

    def test_add_os(self):

        firefox = BrowserFactory.create_browser("Firefox", save=False)
        BrowserFactory.save_browser(firefox)

        # this works
        assert firefox in db.session

    def test_delete_os(self):

        firefox = BrowserFactory.create_browser("Firefox", save=True)
        # this works
        assert firefox in db.session

        was_deleted = BrowserFactory.delete_browser(firefox)

        # this works
        assert was_deleted

    def test_add_twice_os(self):

        BrowserFactory.create_browser("Firefox", save=True)

        firefox2 = BrowserFactory.create_browser("Firefox", save=True)
        assert firefox2 is not None

        firefox_found = BrowserFactory.find_by_name("Firefox")
        # # this works
        assert firefox_found in db.session

    def test_remove_nonexisting_os(self):

        firefox = BrowserFactory.create_browser("Firefox")

        firefox_found = BrowserFactory.delete_browser(firefox)

        # this works
        assert firefox_found

    def test_find_existing(self):
        BrowserFactory.create_browser("Firefox", save=True)
        firefox2 = BrowserFactory.create_browser("Firefox 2", save=True)

        firefox_found = BrowserFactory.find_by_name("Firefox")
        # # this works
        assert firefox_found
        assert firefox_found != firefox2