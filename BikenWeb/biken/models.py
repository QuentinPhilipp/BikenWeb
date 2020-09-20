"""Database models."""
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
	"""User account model."""
	__tablename__ = 'flasklogin-users'
	id = db.Column(
		db.Integer,
		primary_key=True
	)
	name = db.Column(
		db.String(100),
		nullable=False,
		unique=False
	)
	email = db.Column(
		db.String(40),
		unique=True,
		nullable=False
	)
	password = db.Column(
		db.String(200),
		primary_key=False,
		unique=False,
		nullable=False
	)
	created_on = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )
	last_login = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )
	stravaToken = db.Column(
        db.String(40),
        index=False,
        unique=False,
        nullable=True
    )
	stravaTokenExpiration = db.Column(
        db.Integer,
        index=False,
        unique=False,
        nullable=True
	)
	itinerary = db.relationship("Itinerary")

	def set_password(self, password):
		"""Create hashed password."""
		self.password = generate_password_hash(password, method='sha256')

	def check_password(self, password):
		"""Check hashed password."""
		return check_password_hash(self.password, password)

	def __repr__(self):
		return '<User {}>'.format(self.username)




class Itinerary(db.Model):
	"""User account model."""
	__tablename__ = 'itinerary'
	id = db.Column(
		db.Integer,
        unique=True,
		primary_key=True
	)
	itineraryIdentifier = db.Column(
		db.String(16),
        unique=True
	)
	user_id=db.Column(
		db.Integer,
		db.ForeignKey("flasklogin-users.id")
	)
	polyline=db.Column(
		db.String()
	)
	distance=db.Column(
		db.Float(),
        unique=False,
        nullable=True
	)
	name=db.Column(
		db.String(100),
        unique=False,
        nullable=True
	)
	duration=db.Column(
		db.Integer
	)
