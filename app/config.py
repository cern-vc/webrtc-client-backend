import os


def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


class BaseConfig(object):
    ADMIN_EGROUP = os.environ['ADMIN_EGROUP']
    APP_PORT = int(os.environ['APP_PORT'])

    CACHE_MEMCACHED_SERVERS = ('memcached',)

    CERN_OAUTH_CLIENT_ID = os.environ['CERN_OAUTH_CLIENT_ID']
    CERN_OAUTH_CLIENT_SECRET = os.environ['CERN_OAUTH_CLIENT_SECRET']

    API_OAUTH_CLIENT_ID = os.environ['API_OAUTH_CLIENT_ID']
    API_OAUTH_CLIENT_SECRET = os.environ['API_OAUTH_CLIENT_SECRET']
    API_OAUTH_REDIRECT_URL = os.environ['API_OAUTH_REDIRECT_URL']

    DB_NAME = os.environ['DB_NAME']
    DB_PASS = os.environ['DB_PASS']
    DB_PORT = os.environ['DB_PORT']
    DB_SERVICE = os.environ['DB_SERVICE']
    DB_USER = os.environ['DB_USER']

    DEBUG = str2bool(os.environ['DEBUG'])

    IS_DEV_INSTALLATION = str2bool(os.environ['IS_DEV_INSTALLATION'])
    IS_LOCAL_INSTALLATION = str2bool(os.environ['IS_LOCAL_INSTALLATION'])

    SECRET_KEY = os.environ['SECRET_KEY']

    SENTRY_DSN = os.environ['SENTRY_DSN']
    SENTRY_ENABLED = str2bool(os.environ['SENTRY_ENABLED'])

    SSL_CONTEXT = os.environ['SSL_CONTEXT']

    TESTING = False

    USE_PROXY = str2bool(os.environ['USE_PROXY'])
    ENABLE_PREFIX_MIDDLEWARE = str2bool(os.environ['ENABLE_PREFIX_MIDDLEWARE'])

    SQLALCHEMY_DATABASE_URI = 'mysql://{user}:{password}@{host}:{port}/{db}'.format(
        user=DB_USER, password=DB_PASS, host=DB_SERVICE, port=DB_PORT, db=DB_NAME
    )

    DB_MODELS_IMPORTS = (
        'app.models.users', 'app.models.browser_handling',)

    LANGUAGES = {
        'en': 'English',
        'es': 'Spanish'
    }

