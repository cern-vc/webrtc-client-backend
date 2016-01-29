from logging.handlers import RotatingFileHandler

from flask import logging

from app import create_app

if __name__ == "__main__":
    app = create_app('config')
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.run()
