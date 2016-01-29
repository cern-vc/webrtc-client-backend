.. _api:

=============
API
=============

This is the API

- `browser_handling API`_
- `auth API`_


This API returns always JSON objects. The additional parameters expected can be sent as GET or POST requests.

In case of successful result, the JSON dict will contain the key 'success' with the correspondent value. In case of error, the JSON dict will contain the key 'error' with a description of the error as value.

.. _browser_handling API:

Browser Handling
-----

The entry point for this API is::

    /api/v1.0

Check allowed browser
____

Checks whether a browser version should be allowed or not.

- Function name: **browsers**
- Content-type: application/json
- Parameters (JSON encoded):
    * **browser_name**: Name of the browser (string)
    * **browser_version**: Version of the browser (int)
    * **and_higher**: True if higher versions should be redirected (boolean)

URL specification::

    /browser/

Allowed methods:
- POST

**Example**

URL::

    /api/v1.0/browser/


Headers::

    Accept: application/json
    Content-Type: application/json

Content::

    {
      "browser_name": "Chrome",
      "browser_version": "48",
      "and_higher": true
    }

RESULT::

    {
    "should_redirect": true,
    "system_info": {
        "browser": {
            "name": "Chrome",
            "version": "48"
        },
        "os": {
            "name": "Mac OS",
            "version": "X 10.11.2"
        }
    }
}

Notes: Remember to add the final trailing slash.

.. _auth API:

API Auth
-----

The entry point for this API is::

    /api/v1.0/auth

Get API JWT
____

Uses the CERN Oauth2 token to verify the user's identity and logs him/her in the application by returning a limited time JWT encoded in base64.

- Function name: **token**
- Content-type: application/json
- Parameters (JSON encoded):
    * **token**: CERN Oauth2 token
- Returns: A JWT base64 encoded.

URL specification::

    /token/

Allowed methods:
- POST

**Example**

URL::

    /api/v1.0/auth/token/


Headers::

    Accept: application/json
    Content-Type: application/json

Content::

    {
      "token": "This is the Oauth2 CERN Token"
    }

RESULT::

    {'success': True, 'token': "This is the JSON Web Token base64 encoded"}


Authentication failed::

    {
      "error": "Authorization has been denied for this request."
    }
Notes: Remember to add the final trailing slash.