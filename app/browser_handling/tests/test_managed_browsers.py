from flask.ext.testing import TestCase
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from app import db

from app.browser_handling.tests import ModelTestCase
from app.browser_handling.models import BrowserFactory, OperatingSystemFactory, ManagedBrowser, ManagedBrowserFactory


class ManagedBrowserTest(ModelTestCase):
    firefox = None
    windows_7 = None
    ubuntu_14 = None

    def setUp(self):
        ModelTestCase.setUp(self)

        self.firefox = BrowserFactory.create_browser(name="Firefox", save=True)
        self.windows_7 = OperatingSystemFactory.create_operating_system(name="Windows 7", save=True)
        self.ubuntu_14 = OperatingSystemFactory.create_operating_system(name="Ubuntu 14", save=True)

    def test_add_managed_browser(self):
        # this works
        assert self.firefox in db.session
        assert self.windows_7 in db.session

        firefox_17 = ManagedBrowser(browser_id=self.firefox.id, version="17", allow_version=False,
                                    op_systems=[self.windows_7, self.ubuntu_14])

        db.session.add(firefox_17)
        db.session.commit()

        assert firefox_17 in db.session
        assert self.windows_7 in firefox_17.operating_systems
        assert self.ubuntu_14 in firefox_17.operating_systems
        assert firefox_17.version == "17"
        assert firefox_17.browser == self.firefox

    def test_remove_managed_browser(self):
        firefox_17 = ManagedBrowser(browser_id=self.firefox.id, version="17", allow_version=False,
                                    op_systems=[self.windows_7])

        db.session.add(firefox_17)
        db.session.commit()

        db.session.delete(firefox_17)
        db.session.commit()

        # this works
        assert firefox_17 not in db.session

    def test_add_twice_browser(self):

        firefox_17 = ManagedBrowser(browser_id=self.firefox.id, version="17", allow_version=False,
                                    op_systems=[self.windows_7])
        db.session.add(firefox_17)
        db.session.commit()

        firefox_17 = ManagedBrowser(browser_id=self.firefox.id, version="17", allow_version=False,
                                    op_systems=[self.windows_7])
        db.session.add(firefox_17)
        db.session.commit()
        try:
            db.session.commit()
            assert True
        except IntegrityError:
            db.session.rollback()
            assert None

        firefox_founds = ManagedBrowser.query.filter_by(browser_id=self.firefox.id, version="17").all()
        # this works
        assert len(firefox_founds) == 2

    def test_remove_unexisting_managed_browser(self):

        firefox_17 = ManagedBrowser(browser_id=self.firefox.id, version="17", allow_version=False,
                                    op_systems=[self.windows_7])
        firefox_18 = ManagedBrowser(browser_id=self.firefox.id, version="18", allow_version=False,
                                    op_systems=[self.windows_7])

        # assert firefox_18 not in db.session
        # assert firefox_17 not in db.session

        try:
            db.session.delete(firefox_17)
            assert None
        except InvalidRequestError:
            assert True
            # db.session.commit()
            #
            # # this works

            # TODO These are on the session, but don't know why.
            # firefox_founds = ManagedBrowser.query.filter_by(browser_id=self.firefox.id).all()
            # print firefox_founds
            # assert firefox_17 not in db.session
            # assert firefox_18 not in db.session


class OperatingSystemFactoryTest(ModelTestCase):
    firefox = None
    windows_7 = None
    ubuntu_14 = None

    def setUp(self):
        ModelTestCase.setUp(self)

        self.firefox = BrowserFactory.create_browser(name="Firefox", save=True)
        self.windows_7 = OperatingSystemFactory.create_operating_system(name="Windows 7", save=True)
        self.ubuntu_14 = OperatingSystemFactory.create_operating_system(name="Ubuntu 14", save=True)

    def test_add_managed_browser(self):
        firefox_17 = ManagedBrowserFactory.create(browser_id=self.firefox.id, version="17",
                                                  allow_version=False,
                                                  op_systems=[self.windows_7, self.ubuntu_14], save=False)
        ManagedBrowserFactory.save(firefox_17)

        # this works
        assert firefox_17 in db.session

    def test_delete_managed_browser(self):
        firefox_17 = ManagedBrowserFactory.create(browser_id=self.firefox.id, version="17",
                                                  allow_version=False,
                                                  op_systems=[self.windows_7, self.ubuntu_14], save=False)
        # this works
        assert firefox_17 in db.session

        was_deleted = BrowserFactory.delete_browser(firefox_17)

        # this works
        assert was_deleted

    def test_remove_nonexisting_managed_browser(self):
        firefox_19 = ManagedBrowserFactory.create(browser_id=self.firefox.id, version="19",
                                                  allow_version=False,
                                                  op_systems=[self.windows_7, self.ubuntu_14], save=False)

        firefox_found = ManagedBrowserFactory.delete(firefox_19)

        # this works
        assert not firefox_found

    # def test_find_existing(self):
    #     firefox_19 = ManagedBrowserFactory.create(browser_id=self.firefox.id, version="19",
    #                                               allow_version=False,
    #                                               op_systems=[self.windows_7, self.ubuntu_14], save=False)
    #
    #     firefox_found = ManagedBrowserFactory.find_by_name_and_version(name="Firefox", version="19")
    #     # # this works
    #     assert firefox_found
