from app.extensions import db

table_prefix = 'bh_'

operating_systems = db.Table(table_prefix + 'operating_systems',
                             db.Column('bh_os_id', db.Integer, db.ForeignKey('bh_operating_system.id')),
                             db.Column('bh_mb_id', db.Integer, db.ForeignKey('bh_managed_browser.id')),
                             )


class OperatingSystem(db.Model):
    """
    Operating System
    """
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
    """
    Browser
    """
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
    """
    A ManagedBrowser is a combination of Browsers and OperatingSystems with versions.
    It will tell the browser_handling API which browser versions are allowed or not.
    """
    __tablename__ = table_prefix + 'managed_browser'
    id = db.Column(db.Integer, primary_key=True)
    browser_id = db.Column(db.Integer, db.ForeignKey('bh_browser.id'), unique=True)

    version = db.Column(db.String(255))
    allow_version = db.Column(db.Boolean)
    allow_higher_versions = db.Column(db.Boolean)
    allow_lower_versions = db.Column(db.Boolean)

    operating_systems = db.relationship('OperatingSystem', secondary=operating_systems,
                                        backref=db.backref('bh_managed_browsers', lazy="dynamic"))

    def __init__(self, browser_id=False, version="", allow_version=False, allow_lower_versions=False, allow_higher_versions=True, operating_systems=[]):
        if not Browser.query.filter_by(id=browser_id).first():
            raise ValueError("No Browser with that id exists")
        self.browser_id = browser_id
        self.version = version
        self.allow_version = allow_version
        self.allow_lower_versions = allow_lower_versions
        self.allow_higher_versions = allow_higher_versions
        self.operating_systems = []

        for operating_system in operating_systems:
            self.operating_systems.append(operating_system)

    def __repr__(self):
        return '<Managed Browser %r>' % self.version
