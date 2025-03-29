from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)



class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String , nullable=False)
    city = db.Column(db.String(120) , nullable=False)
    state = db.Column(db.String(120) , nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # 
    genres = db.Column(db.String(120) , nullable=False)
    website_link=db.Column(db.String(120))
    looking_talent=db.Column(db.Boolean ,default=False)
    seeking_description= db.Column(db.String)

    shows = db.relationship('Show', backref='related_venue', cascade='all, delete-orphan', lazy=True)


   

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String , nullable=False)
    city = db.Column(db.String(120) , nullable=False)
    state = db.Column(db.String(120) , nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120) , nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # 
    website_link=db.Column(db.String(120))
    looking_venues=db.Column(db.Boolean , default=False)
    seeking_description= db.Column(db.String)



class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue = db.relationship('Venue', backref=db.backref('related_shows', cascade='all, delete-orphan', lazy=True))
    artist = db.relationship('Artist', backref='shows', lazy=True)
    