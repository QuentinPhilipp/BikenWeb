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
	userId = db.Column(
		db.String(16),
        unique=True
	)
	name = db.Column(
		db.String(100),
		nullable=False,
		unique=False
	)
	email = db.Column(
		db.String(40),
		unique=True
	)
	password = db.Column(
		db.String(200),
		primary_key=False,
		unique=False,
		nullable=False
	)
	createdOn = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )
	lastLogin = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )
	stravaId = db.Column(
        db.Integer,
        index=False,
        unique=True
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
	polyline=db.Column(
		db.String()
	)
	distance=db.Column(
		db.Float(),
        unique=False,
        nullable=True
	)
	duration=db.Column(
		db.Integer
	)
	startCoordLat=db.Column(
		db.Float()
	)
	startCoordLon=db.Column(
		db.Float()
	)	
	endCoordLat=db.Column(
		db.Float()
	)	
	endCoordLon=db.Column(
		db.Float()
	)
class ItineraryOwnership(db.Model):
	"""Define the appartenance of itinerary to different user"""
	__tablename__ = 'itineraryOwnership'
	id = db.Column(
		db.Integer,
        unique=True,
		primary_key=True
	)
	itineraryIdentifier = db.Column(
		db.String(16)
	)
	userId = db.Column(
		db.String(16)
	)
	private = db.Column(
		db.Boolean
	)
	name = db.Column(
		db.String(100)
	)