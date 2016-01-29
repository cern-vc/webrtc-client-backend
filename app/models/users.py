from flask_login import UserMixin
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin
from app.extensions import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    __table_args__ = (db.CheckConstraint('email = lower(email)', 'lowercase_email'),)

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    first_name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())

    @property
    def name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __repr__(self):
        admin = ', is_admin=True' if self.is_admin else ''
        return '<User({}, {}, person_id={}{}): {}>'.format(self.id, self.email, self.person_id, admin, self.name)

    @staticmethod
    def create_from_auth_data(data, is_admin=False, *args):
        """Create a user using data received during authentication.

        :param data: A dict containing ``person_id``, ``first_name``,
                     ``last_name`` and ``email``.
        :param is_admin: Whether the user is be an admin or not
        :return: a new `User` instance
        """
        user = User(person_id=data['person_id'], first_name=data['first_name'], last_name=data['last_name'],
                    email=data['email'].lower(), is_admin=is_admin)
        db.session.add(user)
        db.session.commit()
        return user

    def tojson(self):
        return {'id': self.id, 'first_name': self.first_name, 'last_name': self.last_name, 'email': self.email,
                'is_admin': self.is_admin}


class OAuth(db.Model, OAuthConsumerMixin):
    __tablename__ = 'flask_dance_oauth'

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
