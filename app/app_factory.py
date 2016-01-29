import sys
from importlib import import_module

from flask import Flask, render_template, request, session, redirect

from werkzeug.contrib.fixers import ProxyFix

from app.extensions import db, sentry, babel, cache
from app.common.cern_oauth import load_cern_oauth
from app.static_assets import register_assets
from flask_cors import CORS


class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]


def create_app(config_filename):
    """
    Factory to create the application using a file
    :param config_filename: The name of the file that will be used for configuration.
    :return: The created application
    """

    application = Flask(__name__)
    application.config.from_object(config_filename)

    CORS(application)

    if application.config.get('ENABLE_PREFIX_MIDDLEWARE', False):
        application.wsgi_app = PrefixMiddleware(application.wsgi_app, prefix=application.config.get("APPLICATION_ROOT", "/"))

        # setup_webapp_handlers(app)
    if application.config.get('USE_PROXY', False):
        application.wsgi_app = ProxyFix(application.wsgi_app)

    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False

    cache.init_app(application)

    with application.app_context():
        for module in application.config.get('DB_MODELS_IMPORTS', list()):
            import_module(module, application)

    load_cern_oauth(application)

    register_assets(application)

    db.init_app(application)
    babel.init_app(application)

    if not application.config['DEBUG'] and not application.config['TESTING']:
        if not application.config['SECRET_KEY']:
            print('Error: You should set up a secret key')
            sys.exit(1)

    if application.config['SENTRY_ENABLED']:
        if application.config.get('SENTRY_DSN', None):
            sentry.init_app(application)
        else:
            raise ValueError("Sentry is enabled but DSN is not setup.")

    _initialize_views(application)

    _initialize_api_blueprints(application)

    with application.app_context():
        db.create_all()

    @application.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(application.config.get('LANGUAGES').keys())

    @application.context_processor
    def inject_conf_var():

        return dict(IS_DEV_INSTALLATION=application.config.get('IS_DEV_INSTALLATION'),
                    IS_LOCAL_INSTALLATION=application.config.get('IS_LOCAL_INSTALLATION'))

    return application


def _initialize_views(application):
    from app.views.common import mod as main_module
    from app.views.browser_handling import mod as browser_handling_module
    from app.views.users import users_bp

    application.register_blueprint(main_module)
    application.register_blueprint(browser_handling_module)
    application.register_blueprint(users_bp)


def _initialize_api_blueprints(application):
    from app.api.resources.api_auth import auth_bp
    from app.api.resources.examples import example_bp
    from app.api.resources.browser_handling import browser_bp

    # API
    application.register_blueprint(auth_bp)
    application.register_blueprint(example_bp)
    application.register_blueprint(browser_bp)
