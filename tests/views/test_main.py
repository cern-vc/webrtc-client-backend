from tests import BaseTestCase
from flask import url_for


class LogoutTest(BaseTestCase):
    def test_index_redirected(self):
        response = self.client.get(url_for('users.logout'))
        self.assertEqual(response.status_code, 302)
