import httpagentparser
from flask import request, jsonify, Blueprint
from flask.ext.restful import reqparse
from flask_restful import Resource, Api

from app.models.browser_handling import ManagedBrowser, Browser

browser_bp = Blueprint('browser_api', __name__)
api = Api(browser_bp)


class BrowserHandlingApi(Resource):
    """
        Class that manages the browser handling API
    """

    def __init__(self):
        """
            Initializes the class instance with a request parser validator.

            The class requires a browser_name and a browser_vesion.
        :return: The class instance
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('browser_name', type=str, required=True,
                                   help='No browser name provided', location='json')
        self.reqparse.add_argument('browser_version', type=int, required=True,
                                   help='No browser version provided', location='json')
        super(BrowserHandlingApi, self).__init__()

    def post(self):
        """
            Gets the browser name and version and tells if the user should be redirected.
        :return: A JSON response telling if the user should be redirected to the Vidyoportal
        """
        s = request.headers.get('User-Agent')

        args = self.reqparse.parse_args()

        browser_name = args['browser_name']
        browser_version = int(args['browser_version'])

        browser_info = httpagentparser.detect(s)
        os_name = browser_info['platform']['name']
        os_version = browser_info['platform']['version']

        should_redirect = False
        browser = Browser.query.filter_by(name=browser_name).first()

        if browser:
            managed_browser = ManagedBrowser.query.filter_by(browser_id=browser.id).first()

            if managed_browser:
                managed_browser_version = int(managed_browser.version)

                if browser_version == managed_browser_version and not managed_browser.allow_version:
                    should_redirect = True
                elif browser_version < managed_browser_version and not managed_browser.allow_lower_versions:
                    should_redirect = True
                elif browser_version > managed_browser_version and not managed_browser.allow_higher_versions:
                    should_redirect = True

        return jsonify(
            {'should_redirect': should_redirect,
             'system_info': {'browser': {'name': browser_name, 'version': browser_version},
                             'os': {'name': os_name, 'version': os_version}}})


api.add_resource(BrowserHandlingApi, '/api/v1.0/browser/', endpoint='BrowserHandlingApi')
