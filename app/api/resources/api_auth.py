import os

from flask.ext.restful import reqparse
from flask_restful import Resource, Api

import json
from flask import Blueprint, abort, current_app, jsonify

from itsdangerous import TimedSerializer, BadSignature
from httplib2 import Http
from oauth2client.client import OAuth2WebServerFlow

auth_bp = Blueprint('auth_api', __name__)
api = Api(auth_bp)


def _get_token_serializer():
    return TimedSerializer(current_app.config['SECRET_KEY'])


def _get_oauth2_identity(auth_code):
    client_id = current_app.config.get('API_OAUTH_CLIENT_ID')
    client_secret = current_app.config.get('API_OAUTH_CLIENT_SECRET')
    redirect_url = current_app.config.get('API_OAUTH_REDIRECT_URL')
    info = ""
    if not client_id:
        # Error - No OAuth2 client id configured
        return

    if not client_secret:
        # Error - No OAuth2 client secret configured
        return

    flow = OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        auth_uri=os.environ['CERN_OAUTH_AUTHORIZE_URL'],
        token_uri=os.environ['CERN_OAUTH_TOKEN_URL'],
        scope='bio',
        redirect_uri=redirect_url)

    credentials = flow.step2_exchange(auth_code)

    info = _get_user_info(credentials)
    return info


def _get_user_info(credentials):
    http_client = Http()
    if credentials.access_token_expired:
        credentials.refresh(http_client)
    credentials.authorize(http_client)

    response, response_body = http_client.request(os.environ['CERN_OAUTH_API_ME'], "GET")
    return _process_user_info(json.loads(response_body))
    # return ""


def _process_user_info(user_info):
    displayName = None
    username = None
    employeeID = None
    email = None
    departament = None
    group = None
    first_name = None
    try:
        if user_info["Message"]:
            return json.dumps({'error': '%s' % user_info["Message"]})
    except TypeError:
        pass

    for value in user_info:
        if value["Type"] == "http://schemas.xmlsoap.org/claims/CommonName":
            username = value["Value"]
        if value["Type"] == "http://schemas.xmlsoap.org/claims/PersonID":
            employeeID = value["Value"]
        if value["Type"] == "http://schemas.xmlsoap.org/claims/EmailAddress":
            email = value["Value"]
        if value["Type"] == "http://schemas.xmlsoap.org/claims/DisplayName":
            displayName = value["Value"]
        if value["Type"] == "http://schemas.xmlsoap.org/claims/Department":
            departament = value["Value"]
        if value["Type"] == "http://schemas.xmlsoap.org/claims/Group":
            group = value["Value"]
        if value["Type"] == "http://schemas.xmlsoap.org/claims/Firstname":
            first_name = value["Value"]

    result = {"username": username, "displayName": displayName, "firstName": first_name, "employeeID": employeeID, "email": email,
              "department": departament, "group": group}

    return result


class AuthApi(Resource):
    """
        Class that manages the browser handling API
    """

    def __init__(self):
        """
            Initializes the class instance.

        :return: The class instance
        """

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('authorizationCode', type=str, required=True,
                                   help='No authorizationCode provided', location='json')

        super(AuthApi, self).__init__()

    def post(self):
        """

        Tries to make a request to the CERN Oauth2 API Url and retrieve some user information with the given user token.
        If the token is not valid means that the user is not valid and will be rejected.

        :return: The generated token for the user or an error.
        """
        args = self.reqparse.parse_args()

        auth_code = args['authorizationCode']

        if auth_code is None:
            abort(401)

        user_info = _get_oauth2_identity(auth_code)
        if not user_info:
            abort(401)

        token = _get_token_serializer().dumps({'user_info': user_info})

        return jsonify({
            'auth_token': token,
            'user_info': user_info,
        })


class ReauthApi(Resource):
    """
        Class that manages the browser handling API
    """

    def __init__(self):
        """
            Initializes the class instance.

        :return: The class instance
        """

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('auth_token', type=str, required=True,
                                   help='No auth_token provided', location='json')

        super(ReauthApi, self).__init__()

    def post(self):
        """

        Tries to make a request to the CERN Oauth2 API Url and retrieve some user information with the given user token.
        If the token is not valid means that the user is not valid and will be rejected.

        :return: The generated token for the user or an error.
        """
        args = self.reqparse.parse_args()

        token = args['auth_token']

        if token is None:
            abort(401)
        try:
            token_data = _get_token_serializer().loads(
                token, max_age=current_app.config['_MAX_TOKEN_AGE'])
        except BadSignature:
            abort(401)

        return jsonify({
            'auth_token': token,
            'user_info': token_data['user_info'],
        })


api.add_resource(AuthApi, '/api/v1.0/auth/login/', endpoint='AuthApi')
api.add_resource(ReauthApi, '/api/v1.0/auth/reauth/', endpoint='ReauthApi')