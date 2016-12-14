import os
from flask import flash, current_app
from flask_dance import OAuth2ConsumerBlueprint
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_login import (
    LoginManager, current_user, login_user
)
from sqlalchemy.orm.exc import NoResultFound

from app.extensions import db
from app.models.users import User, OAuth


def load_cern_oauth(app):
    oauth = OAuth2ConsumerBlueprint(
        'cern_oauth',
        __name__,
        url_prefix='/oauth',
        # oauth specific settings
        token_url=os.environ['CERN_OAUTH_TOKEN_URL'],
        authorization_url=os.environ['CERN_OAUTH_AUTHORIZE_URL'],
        # local urls
        login_url='/cern',
        authorized_url='/cern/authorized',
        client_id=app.config.get('CERN_OAUTH_CLIENT_ID', ''),
        client_secret=app.config.get('CERN_OAUTH_CLIENT_SECRET', '')
    )

    app.register_blueprint(oauth)

    oauth.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)

    # setup login manager
    login_manager = LoginManager()
    login_manager.login_view = 'cern_oauth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.init_app(app)

    @oauth_authorized.connect_via(oauth)
    def cern_logged_in(bp, token):
        # We don't keep the OAuth token since it's excessively long (~3kb) and we don't need
        # it anymore after getting the data here.
        response = oauth.session.get('https://oauthresource.web.cern.ch/api/User')
        egroups_info = oauth.session.get('https://oauthresource.web.cern.ch/api/Groups')
        is_admin = False
        for egroup in egroups_info.json()['groups']:
            if egroup == current_app.config.get('ADMIN_EGROUP'):
                is_admin = True
                break

        response.raise_for_status()
        data = response.json()
        flash("You are {first_name}".format(first_name=data['first_name'].strip()))

        query = User.query.filter_by(username=data['username'].strip())
        try:
            existing_user = query.one()

        except NoResultFound:
            existing_user = User(username=data['username'].strip(), person_id=data['personid'],
                                 email=data['email'].strip(),
                                 last_name=data['last_name'].strip(),
                                 first_name=data['first_name'].strip(),
                                 is_admin=is_admin)
            db.session.add(existing_user)
            db.session.commit()
        if login_user(existing_user):
            existing_user.is_admin=is_admin
            flash("Successfully signed in")
        db.session.commit()

        app.logger.info('OAuth login successful for %s (%s #%d)', data['username'], data['email'],
                        data['personid'])