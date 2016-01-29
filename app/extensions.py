from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
from flask_babel import Babel
from flask_caching import Cache


"""
All the extensions are loaded here except the Api, which is loaded using different blueprints
on the api module.
"""
db = SQLAlchemy()
sentry = Sentry()
babel = Babel()

cache = Cache(config={'CACHE_TYPE': 'memcached'})
