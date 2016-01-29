from functools import wraps
from flask import redirect, session, abort
from flask import current_app


def requires_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user', None) and not current_app.config['DEBUG'] and not current_app.config['TESTING']:
            return redirect(current_app.config["SSO_LOGIN_URL"])
        return f(*args, **kwargs)
    return decorated_function


# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         testing = False
#         if current_app.config['IS_LOCAL_INSTALLATION'] or current_app.config['IS_TESTING']:
#             testing = True
#         if not testing:
#             if not (session.get('user', False) and session.get('is_admin', False)):
#                 abort(401)
#         return f(*args, **kwargs)
#     return decorated_function
