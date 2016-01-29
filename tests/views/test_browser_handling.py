from sqlalchemy.exc import IntegrityError, InvalidRequestError

from app.extensions import db
from app.models.browser_handling import OperatingSystem, Browser, ManagedBrowser
from tests import BaseTestCase
from flask import url_for


class HomeTest(BaseTestCase):
    def test_index_redirected(self):
        response = self.client.get(url_for('main.index'))
        self.assertEqual(response.status_code, 302)

    def test_home_reachable(self):
        response = self.client.get(url_for('main.home'))
        self.assertEqual(response.status_code, 200)


class ManagedBrowsersListTest(BaseTestCase):
    def test_list_reachable(self):
        response = self.client.get(url_for('browser_handling.list_all'))
        self.assertEqual(response.status_code, 200)


class ManagedBrowsersFormsListTest(BaseTestCase):
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

    def test_list_reachable(self):
        response = self.client.get(url_for('browser_handling.list_all'))
        self.assertEqual(response.status_code, 200)

    def test_add_managed_browser(self):
        response = self.client.get(url_for('browser_handling.list_all'))
        self.assertEqual(response.status_code, 200)

        managed_browser_form_data = {"add_managed_browser_id": self.firefox.id,
                                     "add_managed_browser_version": "33",
                                     "add_managed_browser_disabled": True,
                                     "add_operating_systems": [self.windows_7.id, self.ubuntu_14.id]}

        self.client.post(url_for('browser_handling.list_all'), data=managed_browser_form_data, follow_redirects=True)
        os = ManagedBrowser.query.filter_by(browser_id=self.firefox.id, version="33").first()
        self.assertIsNotNone(os)

        print os.operating_systems
        self.assertEqual(len(os.operating_systems), 2)

    def test_edit_managed_browser(self):
        response = self.client.get(url_for('browser_handling.list_all'))
        self.assertEqual(response.status_code, 200)

        managed_browser_form_data = {"add_managed_browser_id": self.firefox.id,
                                     "add_managed_browser_version": "33",
                                     "add_managed_browser_disabled": True}

        self.client.post(url_for('browser_handling.list_all'), data=managed_browser_form_data, follow_redirects=True)
        os = ManagedBrowser.query.filter_by(browser_id=self.firefox.id, version="33").first()
        self.assertIsNotNone(os)

        new_managed_browser_form_data = {
            "edit_managed_browser_id": os.id,
            "edit_managed_browser_browser_id": self.firefox.id,
            "edit_managed_browser_version": "34",
            "edit_managed_browser_disabled": False,
            "edit_operating_systems": [self.windows_7.id, self.ubuntu_14.id]}

        print new_managed_browser_form_data

        self.client.post(url_for('browser_handling.list_all'), data=new_managed_browser_form_data,
                         follow_redirects=True)
        os2 = ManagedBrowser.query.filter_by(browser_id=self.firefox.id, version="34").first()
        self.assertIsNotNone(os2)
        self.assertEqual(os2.version, "34")
        print os2.operating_systems
        self.assertEqual(len(os2.operating_systems), 2)


class ManagedBrowsersFormDeleteListTest(BaseTestCase):
    firefox = None
    windows_7 = None
    ubuntu_14 = None

    def setUp(self):
        BaseTestCase.setUp(self)

        self.firefox = Browser(name="Firefox")
        self.windows_7 = OperatingSystem(name="Windows 7")
        self.ubuntu_14 = OperatingSystem(name="Ubuntu 14")
        #
        db.session.add(self.firefox)
        db.session.add(self.windows_7)
        db.session.add(self.ubuntu_14)
        opera = Browser(name="Opera")
        db.session.add(opera)
        db.session.commit()
        opera_managed = ManagedBrowser(browser_id=1, version="33", allow_version=True)
        # #
        db.session.add(opera_managed)
        db.session.commit()

    def test_delete_managed_browser(self):
        managed_browser_form_data = {"managed_browser_id": 1}
        # self.assertEquals(managed_browser.id, 1)

        client = self.app.test_client()
        response = client.post(url_for('browser_handling.list_all'), data=managed_browser_form_data)
        print response
        self.assertIsNone(ManagedBrowser.query.get(1))


class ConfigurationTest(BaseTestCase):
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

    def test_config_reachable(self):
        response = self.client.get(url_for('browser_handling.configuration'))
        self.assertEqual(response.status_code, 200)

    def test_config_add_operating_system(self):
        response = self.client.get(url_for('browser_handling.configuration'))
        self.assertEqual(response.status_code, 200)

        os_form_data = {"add_os_form-operating_system_name": "Windows"}
        self.client.post(url_for('browser_handling.configuration'), data=os_form_data, follow_redirects=True)
        os = OperatingSystem.query.filter_by(name="Windows").first()
        self.assertIsNotNone(os)

        os_form_data = {"add_os_form-operating_system_name": "Windows"}
        response = self.client.post(url_for('browser_handling.configuration'), data=os_form_data, follow_redirects=True)
        print response.data
        self.assertIn("Unable to add Operating System", response.data)

    def test_config_add_browser(self):
        response = self.client.get(url_for('browser_handling.configuration'))
        self.assertEqual(response.status_code, 200)

        browser_form_data = {"add_browser_form-browser_name": "Firefox"}

        response = self.client.post(url_for('browser_handling.configuration'), data=browser_form_data,
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        browser = Browser.query.filter_by(name="Firefox").first()
        self.assertIsNotNone(browser)

        browser_form_data = {"add_browser_form-browser_name": "Firefox"}
        response = self.client.post(url_for('browser_handling.configuration'), data=browser_form_data,
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Unable to add Browser", response.data)

    def test_remove_operating_system(self):
        response = self.client.get(url_for('browser_handling.configuration'))
        self.assertEqual(response.status_code, 200)

        os = OperatingSystem.query.filter_by(name="Windows 7").first()
        self.assertEqual(os.disabled, False, "Operating System should be enabled")
        os_form_data = {"operating_system_id": os.id}

        self.client.post(url_for('browser_handling.configuration'), data=os_form_data, follow_redirects=True)

        os = OperatingSystem.query.filter_by(name="Windows 7").first()

        self.assertEqual(os.disabled, True, "Operating System should be disabled")

    def test_remove_browser(self):
        response = self.client.get(url_for('browser_handling.configuration'))
        self.assertEqual(response.status_code, 200)

        browser = Browser.query.filter_by(name="Firefox").first()
        self.assertEqual(browser.disabled, False, "Browser System should be enabled")
        browser_form_data = {"browser_id": browser.id}

        response = self.client.post(url_for('browser_handling.configuration'), data=browser_form_data,
                                    follow_redirects=True)
        browser = Browser.query.filter_by(name="Firefox").first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(browser.disabled, True, "Browser System should be disabled")
        self.assertIn("Browser was successfully deleted", response.data)

        response = self.client.post(url_for('browser_handling.configuration'), data=browser_form_data,
                                    follow_redirects=True)
        browser = Browser.query.filter_by(name="Firefox").first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(browser.disabled, True, "Browser System should be disabled")
        self.assertIn("Unable to delete Browser", response.data)
