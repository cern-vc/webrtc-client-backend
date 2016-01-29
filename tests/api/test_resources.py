import json

from app.extensions import db
from app.models.browser_handling import Browser, OperatingSystem, ManagedBrowser
from tests import BaseTestCase


class ApiExamplesTest(BaseTestCase):
    def test_example_hello(self):
        response = self.client.get("/api/v1.0/hello/")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(json.loads(response.data), json.loads('{"hello": "world"}'))


class ApiBrowserHandling(BaseTestCase):
    firefox = None
    windows_7 = None
    ubuntu_14 = None
    firefox_17 = None

    def setUp(self):
        BaseTestCase.setUp(self)

        self.firefox = Browser(name="Firefox")
        self.windows_7 = OperatingSystem(name="Windows 7")
        self.ubuntu_14 = OperatingSystem(name="Ubuntu 14")

        db.session.add(self.firefox)
        db.session.add(self.windows_7)
        db.session.add(self.ubuntu_14)
        db.session.commit()

        self.firefox_17 = ManagedBrowser(browser_id=self.firefox.id, version="17", allow_version=False,
                                         operating_systems=[self.windows_7, self.ubuntu_14])

        db.session.add(self.firefox_17)
        db.session.commit()

    def test_browser_handling(self):
        response = self.client.get("/api/v1.0/browser/")
        self.assertEqual(response.status_code, 405)

        response = self.client.post("/api/v1.0/browser/")
        self.assertEqual(response.status_code, 400)

        response = self.client.post("/api/v1.0/browser/", data='{"browser_name": "Firefox", "browser_version": "1"}',
                                    headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)["should_redirect"], True)

        response = self.client.post("/api/v1.0/browser/",
                                    data='{"browser_name": "' + self.firefox.name + '", "browser_version": "' + self.firefox_17.version + '"}',
                                    headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)["should_redirect"], True)

        response = self.client.post("/api/v1.0/browser/",
                                    data=json.dumps({"browser_name": self.firefox.name,
                                                    "browser_version": int(self.firefox_17.version) + 1,
                                                    "and_higher": True}),
                                    headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)["should_redirect"], False)


from httmock import urlmatch, response


@urlmatch(netloc=r'(.*\.)?oauthresource\.web\.cern\.ch$')
def cern_oauth_api_mock(url, request):
    headers = {'content-type': 'application/json'}
    content = [{'Type': '"http://schemas.xmlsoap.org/claims/CommonName"', "Value": "CommonNameMockup"}]
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r'(.*\.)?oauthresource\.web\.cern\.ch$')
def cern_oauth_api_error_mock(url, request):
    headers = {'content-type': 'application/json'}
    content = {'Message': "This is a error"}
    return response(401, content, headers, None, 5, request)
