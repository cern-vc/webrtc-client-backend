from functools import wraps
from flask import redirect, abort, url_for
from flask import current_app
from flask_login import current_user


def requires_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated \
                and not current_app.config['IS_LOCAL_INSTALLATION']\
                and not current_app.config['TESTING']:
            return redirect(url_for('cern_oauth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        testing = False
        if current_app.config['IS_LOCAL_INSTALLATION'] or current_app.config['TESTING']:
            testing = True
        if not testing:
            if not (current_user.is_authenticated and current_user.is_admin):
                abort(401)
        return f(*args, **kwargs)
    return decorated_function
