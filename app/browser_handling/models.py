from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

from app import db
from flask import current_app

table_prefix = 'bh_'

operating_systems = db.Table(table_prefix + 'operating_systems',
                             db.Column('bh_os_id', db.Integer, db.ForeignKey('bh_operating_system.id')),
                             db.Column('bh_mb_id', db.Integer, db.ForeignKey('bh_managed_browser.id')),
                             )


class OperatingSystem(db.Model):
    __tablename__ = table_prefix + 'operating_system'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    disabled = db.Column(db.Boolean)

    def __init__(self, name=None, disabled=False):
        self.name = name
        self.disabled = disabled

    def __repr__(self):
        return '<OS %r>' % self.name


class Browser(db.Model):
    __tablename__ = table_prefix + 'browser'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    disabled = db.Column(db.Boolean)

    managed_browsers = db.relationship('ManagedBrowser', backref='browser', lazy='dynamic')

    def __init__(self, name=None, disabled=False):
        self.name = name
        self.disabled = disabled

    def __repr__(self):
        return '<Browser %r>' % self.name


class ManagedBrowser(db.Model):
    __tablename__ = table_prefix + 'managed_browser'
    id = db.Column(db.Integer, primary_key=True)
    browser_id = db.Column(db.Integer, db.ForeignKey('bh_browser.id'))

    version = db.Column(db.String(255))
    allow_version = db.Column(db.Boolean)

    operating_systems = db.relationship('OperatingSystem', secondary=operating_systems,
                                        backref=db.backref('bh_managed_browsers', lazy="dynamic"))

    def __init__(self, browser_id=False, version="", allow_version=False, op_systems=[]):
        self.browser_id = browser_id
        self.version = version
        self.allow_version = allow_version
        self.operating_systems = []

        for operating_system in op_systems:
            self.operating_systems.append(operating_system)

    def __repr__(self):
        return '<Managed Browser %r>' % (self.version)


class OperatingSystemFactory(object):
    @classmethod
    def create_operating_system(cls, name=None, save=False):
        existing_system = None
        try:
            existing_system = OperatingSystem.query.filter_by(name=name).one()
        except NoResultFound:
            pass
        if existing_system:
            existing_system.disabled = False
            db.session.commit()
            return existing_system
        else:
            new_operating_system = OperatingSystem(name)
        if save:
            was_saved = OperatingSystemFactory.save_operating_system(new_operating_system)
            if not was_saved:
                return None
        return new_operating_system

    @classmethod
    def save_operating_system(cls, operating_system):
        try:
            db.session.add(operating_system)
            db.session.commit()
            return True
        except IntegrityError:
            current_app.logger.error("Tried to add already existing Operating System: %s. Rolling back...",
                                     operating_system.name)
            db.session.rollback()
            return None

    @classmethod
    def delete_operating_system(cls, operating_system):
        try:
            # db.session.delete(operating_system)
            operating_system.disabled = True
            db.session.commit()
            return True
        except InvalidRequestError:
            current_app.logger.error("Tried to remove non existing Operating System: %s", operating_system.name)
            return None

    @classmethod
    def find_by_name(cls, name=""):
        operating_system = None
        try:
            operating_system = OperatingSystem.query.filter_by(name=name, disabled=False).one()
        except NoResultFound:
            current_app.logger.error("Operating System with name: %s doesn't exist", name)

        return operating_system

    @classmethod
    def find_by_id(cls, operating_system_id=""):
        operating_system = None
        try:
            operating_system = OperatingSystem.query.filter_by(id=operating_system_id, disabled=False).one()
        except NoResultFound:
            current_app.logger.error("Operating System with id: %s doesn't exist", operating_system_id)

        return operating_system

    @classmethod
    def fetch_all(cls):
        return OperatingSystem.query.filter_by(disabled=False)


class BrowserFactory(object):
    @classmethod
    def create_browser(cls, name=None, save=False):
        existing_browser = None
        try:
            existing_browser = Browser.query.filter_by(name=name).one()
        except NoResultFound:
            pass
        if existing_browser:
            existing_browser.disabled = False
            db.session.commit()
            return existing_browser
        else:
            new_browser = Browser(name)
        if save:
            was_saved = BrowserFactory.save_browser(new_browser)
            if not was_saved:
                return None
        return new_browser

    @classmethod
    def save_browser(cls, browser):
        try:
            db.session.add(browser)
            db.session.commit()
            return True
        except IntegrityError:
            current_app.logger.error("Tried to add already existing Browser: %s. Rolling back...",
                                     browser.name)
            db.session.rollback()
            return None

    @classmethod
    def delete_browser(cls, browser):
        try:
            # db.session.delete(operating_system)
            browser.disabled = True
            db.session.commit()
            return True
        except InvalidRequestError:
            current_app.logger.error("Tried to remove non existing Browser: %s", browser.name)
            return None

    @classmethod
    def find_by_name(cls, name=""):
        browser = None
        try:
            browser = Browser.query.filter_by(name=name, disabled=False).one()
        except NoResultFound:
            current_app.logger.error("Browser with name: %s doesn't exist", name)

        return browser

    @classmethod
    def find_by_id(cls, browser_id=""):
        browser = None
        try:
            browser = Browser.query.filter_by(id=browser_id, disabled=False).one()
        except NoResultFound:
            current_app.logger.error("Browser with id: %s doesn't exist", browser_id)

        return browser

    @classmethod
    def fetch_all(cls):
        return Browser.query.filter_by(disabled=False)


class ManagedBrowserFactory(object):
    @classmethod
    def create(cls, browser_id=None, version="", allow_version=False, op_systems=[], save=False):
        managed_browser = ManagedBrowser(browser_id=browser_id, version=version,
                                         allow_version=allow_version,
                                         op_systems=op_systems)
        if save:
            was_saved = ManagedBrowserFactory.save(managed_browser)
            if not was_saved:
                return None
        return managed_browser

    @classmethod
    def update(cls, managed_browser_id=None, browser_id=None, version="", allow_version=False, op_systems=[]):

        managed_browser = ManagedBrowserFactory.find_by_id(managed_browser_id)

        if managed_browser:
            current_app.logger.debug("Managed Browser exists")
            managed_browser.browser_id = browser_id
            managed_browser.version = version
            managed_browser.allow_version = allow_version
            managed_browser.operating_systems = op_systems
            db.session.commit()

        return managed_browser

    @classmethod
    def save(cls, managed_browser):
        try:
            db.session.add(managed_browser)
            db.session.commit()
            return True
        except IntegrityError:
            current_app.logger.error("Managed Browser cannot be added. Rolling back...")
            db.session.rollback()
            return None

    @classmethod
    def delete(cls, managed_browser):

        try:
            db.session.delete(managed_browser)
            db.session.commit()
            return True
        except InvalidRequestError:
            current_app.logger.error("Tried to remove non existing Browser: %r", managed_browser)
            return None

    @classmethod
    def fetch_all(cls):
        return ManagedBrowser.query.filter_by()

    @classmethod
    def find_by_id(cls, browser_id=""):
        managed_browser = None
        try:
            managed_browser = ManagedBrowser.query.filter_by(id=browser_id).one()
        except NoResultFound:
            current_app.logger.error("Managed Browser with id: %s doesn't exist", browser_id)

        return managed_browser

        # @classmethod
        # def find_by_name_and_version(cls, name="", version=""):
        #     managed_browsers = None
        #     try:
        #         managed_browsers = Browser.query.filter_by(Browser.name=name, version=version).all()
        #     except NoResultFound:
        #         current_app.logger.error("Browser with name: %s doesn't exist", name)
        #
        #     return managed_browsers
