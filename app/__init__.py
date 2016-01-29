import os
import sys

from flask import Flask, render_template, request as req
from flask.ext.sqlalchemy import SQLAlchemy
from flask_sso import SSO
from flask_restful import Api
from app.api.resources.examples import HelloWorld


# Later on you'll import the other blueprints the same way:
# from app.comments.views import mod as commentsModule
# from app.posts.views import mod as postsModule
# app.register_blueprint(commentsModule)
# app.register_blueprint(postsModule)

ext = SSO(app=None)
app = None
db = SQLAlchemy()


########################
# Configure Secret Key #
########################
def install_secret_key(app, filename='secret_key'):
    """Configure the SECRET_KEY from a file
    in the instance directory.

    If the file does not exist, print instructions
    to create it from a shell with a random key,
    then exit.
    """
    filename = os.path.join(app.instance_path, filename)

    try:
        app.config['SECRET_KEY'] = open(filename, 'rb').read()
    except IOError:
        print('Error: No secret key. Create it with:')
        full_path = os.path.dirname(filename)
        if not os.path.isdir(full_path):
            print('mkdir -p {filename}'.format(filename=full_path))
        print('head -c 24 /dev/urandom > {filename}'.format(filename=filename))
        sys.exit(1)


def create_app(config_filename):

    global ext, app, db

    app = Flask(__name__)

    app.config.from_object(config_filename)

    db = SQLAlchemy(app)
    api = Api(app)

    if not app.config['DEBUG'] and not app.config['TESTING']:
        install_secret_key(app)

    if not app.config['DEBUG'] and not app.config['TESTING']:
        if app.config['SSO_ADMIN_USERGROUP']:
            ext = SSO(app=app)
        else:
            print('Error: SSO_ADMIN_USERGROUP must be set on not DEBUG environments')
            sys.exit(1)

    # from app.users.views import mod as users_module
    # app.register_blueprint(users_module)

    from app.views import mod as main_module
    app.register_blueprint(main_module)

    from app.browser_handling.views import mod as browser_handling_module
    app.register_blueprint(browser_handling_module)

    api.add_resource(HelloWorld, '/hello', '/hello')  # Application context

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    # Logging
    @app.after_request
    def log_response(resp):
        app.logger.info("{} {} {}\n{}".format(req.method, req.url, req.data, resp))
        return resp

    return app
