import os
from webassets import Bundle
from flask_assets import Environment

_basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def register_assets(app):

    assets = Environment(app)

    assets.load_path = [
        os.path.join(os.path.dirname(__file__))
    ]

    assets.register(
        'js_all',
        Bundle(
               '../node_modules/jquery/dist/jquery.min.js',
               '../node_modules/materialize-css/dist/js/materialize.min.js',
               './public/js/main.js',
               output='js/packed.js')
    )

    assets.register(
        'css_all',
        Bundle(
            '../node_modules/materialize-css/dist/css/materialize.min.css',
            './public/css/main.css',
            './public/css/toolbar.css',
            output='css/packed.css')
    )

    return assets