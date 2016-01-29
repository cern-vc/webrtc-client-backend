from sqlalchemy.exc import IntegrityError, InvalidRequestError

from app.extensions import db
from app.models.browser_handling import ManagedBrowser, Browser, OperatingSystem
from tests import BaseTestCase


class ManagedBrowserTest(BaseTestCase):
    firefox = None
    windows_7 = None
    ubuntu_14 = None

    def setUp(self):
        BaseTestCase.setUp(self)

        self.firefox = Browser(name="Firefox")
        self.windows_7 = OperatingSystem(name="Windows 7")
        self.ubuntu_14 = OperatingSystem(name="Ubuntu 14")

        db.session.add(self.firefox)
        db.session.add(self.windows_7)
        db.session.add(self.ubuntu_14)

        db.session.commit()

    def test_add_managed_browser(self):
        # this works
        assert self.firefox in db.session
        assert self.windows_7 in db.session

        firefox_17 = ManagedBrowser(browser_id=self.firefox.id, version="17", allow_version=False,
                                    operating_systems=[self.windows_7, self.ubuntu_14])

        db.session.add(firefox_17)
        db.session.commit()

        assert firefox_17 in db.session
        assert self.windows_7 in firefox_17.operating_systems
        assert self.ubuntu_14 in firefox_17.operating_systems
        assert firefox_17.version == "17"
        assert firefox_17.browser == self.firefox

    def test_remove_managed_browser(self):
        firefox_17 = ManagedBrowser(browser_id=self.firefox.id, version="17", allow_version=False,
                                    operating_systems=[self.windows_7])

        db.session.add(firefox_17)
        db.session.commit()

        db.session.delete(firefox_17)
        db.session.commit()

        # this works
        assert firefox_17 not in db.session

    def test_add_twice_browser(self):

        firefox_17 = ManagedBrowser(browser_id=self.firefox.id, version="17", allow_version=False,
                                    operating_systems=[self.windows_7])
        db.session.add(firefox_17)
        db.session.commit()

        firefox_17 = ManagedBrowser(browser_id=self.firefox.id, version="17", allow_version=False,
                                    operating_systems=[self.windows_7])
        db.session.add(firefox_17)
        # db.session.commit()
        try:
            db.session.commit()
            assert None
        except IntegrityError:
            db.session.rollback()
            assert True

        firefox_founds = ManagedBrowser.query.filter_by(browser_id=self.firefox.id, version="17").all()
        # this works
        assert len(firefox_founds) == 1

    def test_remove_unexisting_managed_browser(self):

        self.assertTrue(self.firefox in db.session)
        self.assertEquals(self.firefox.id, 1)

        firefox_17 = ManagedBrowser(browser_id=1, version="17", allow_version=False)
        firefox_18 = ManagedBrowser(browser_id=1, version="18", allow_version=False)

        db.session.add(firefox_18)
        db.session.commit()

        # assert firefox_18 not in db.session
        self.assertTrue(firefox_17 not in db.session)
        self.assertTrue(firefox_18 in db.session)

        try:
            db.session.delete(firefox_17)
            assert None
        except InvalidRequestError:
            assert True
            db.session.commit()
            #
            # # this works

            # TODO These are on the session, but don't know why.
            assert firefox_17 not in db.session
            assert firefox_18 in db.session
