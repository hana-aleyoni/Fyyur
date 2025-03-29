#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, abort, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import app, db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


moment = Moment(app)

# db.init_app(app)



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# in models.py

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  data=[]
  for venue in venues:
   upcoming_shows= Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
   place = next((a for a in data if a['city'] == venue.city and a['state'] == venue.state), None)
   if place:
    place['venues'].append({
    'id': venue.id,
    'name': venue.name,
    'num_upcoming_shows': upcoming_shows
    })
   else:
    data.append({
    'city': venue.city,
    'state': venue.state,
    'venues': [{
    'id': venue.id,
    'name': venue.name,
    'num_upcoming_shows': upcoming_shows
     }]
})
  return render_template('pages/venues.html',areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
 search_term = request.form.get('search_term', '')
 venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
 response = {
   "count": len(venues),
   "data": [{
   "id": venue.id,
   "name": venue.name,
   "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
   } for venue in venues]
    }
 return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).all() 
  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).all()
  if venue is None:
        abort(404)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','), 
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.looking_talent,
    "seeking_description": venue.seeking_description ,
    "image_link": venue.image_link,
    "past_shows": [{
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
     } for artist, show in past_shows],
    "upcoming_shows": [{
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
     } for artist, show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
     }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  if form.validate():
    try:
      new_venue = Venue(
         name=form.name.data,
         genres=form.genres.data,
         city=form.city.data,
         state=form.state.data,
         address=form.address.data,
         phone=form.phone.data,
         facebook_link=form.facebook_link.data ,
         image_link=form.image_link.data,
         website_link=form.website_link.data,
         looking_talent=form.seeking_talent.data,
         seeking_description= form.seeking_description.data
              )
      db.session.add(new_venue)
      db.session.commit()
  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    except:   
        db.session.rollback()
        flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    finally:
         db.session.close()
  else: 
     flash('an error occurred. please try again')       
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue successfully deleted')
  except:
    db.session.rollback()
    flash('Venue delete failed')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect('/')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
 artists = Artist.query.all()
 data = [{
   'id': artist.id, 
   'name': artist.name} 
   for artist in artists]

 return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response={
    "count": len(artists),
    "data": [{
      "id": artist.id,
      "name":artist.name,
      "num_upcoming_shows": Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.now()).count(),
    }for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.artist_id == artist_id,
        Show.venue_id == Venue.id,
        Show.start_time < datetime.now()
    ).all()
  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.artist_id == artist_id,
        Show.venue_id == Venue.id,
        Show.start_time > datetime.now()
    ).all()
  if artist is None:
        abort(404)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state":artist.state,
    "phone":artist.phone,
    "website_link": artist.website_link,
    "facebook_link":artist.facebook_link,
    "looking_venues": artist.looking_venues ,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link":venue.image_link,
      "start_time":show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }for venue, show in past_shows],
    "upcoming_shows": [{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
     } for venue, show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artists = Artist.query.filter_by(id=artist_id).first()

  if artists is None:
      return abort(404)

  artist = {
      'id': artists.id,
      'name': artists.name,
      'genres': artists.genres.split(', '),
      'city': artists.city,
      'state': artists.state,
      'phone': artists.phone,
      'website_link': artists.website_link,
      'facebook_link': artists.facebook_link,
      'looking_venues': artists.looking_venues,
      'seeking_description': artists.seeking_description,
      'image_link': artists.image_link,
    }

  form = ArtistForm(formdata=None, data=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)

  if artist is None:
      return abort(404)  

  form = ArtistForm(request.form, obj=artist)

  if request.method == 'POST' and form.validate():
      form.populate_obj(artist)
      db.session.commit()
      flash('Artist successfully updated!', 'success')
      return redirect(url_for('show_artist', artist_id=artist_id))
  else:
      return render_template('forms/edit_artist.html', form=form, artist=artist), 400

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venues=Venue.query.filter_by(id=venue_id).first()
  if venues is None:
      return abort(404)
  
  venue={
    "id": venues.id,
    "name":venues.name,
    "genres": venues.genres,
    "address": venues.address,
    "city": venues.city,
    "state": venues.state,
    "phone": venues.phone,
    "website_link": venues.website_link,
    "facebook_link": venues.facebook_link,
    "looking_talent": venues.looking_talent,
    "seeking_description": venues.seeking_description,
    "image_link": venues.image_link
  }
  form = VenueForm(formdata=None, data=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)

  if venue is None:
    return abort(404)
  
  form = VenueForm(request.form, obj=venue)
  if request.method == 'POST' and form.validate():
      form.populate_obj(venue)
      db.session.commit()
      flash('Venue successfully updated!', 'success')
      return redirect(url_for('show_venue', venue_id=venue_id))
  else:
        return render_template('forms/edit_venue.html', form=form, venue=venue), 400

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  if form.validate():
    try:
      new_artist = Artist(
         name=form.name.data,
         city=form.city.data,
         state=form.state.data,
         phone=form.phone.data,
         genres=form.genres.data,
         facebook_link=form.facebook_link.data ,
         image_link=form.image_link.data,
         website_link=form.website_link.data,
         looking_venues=form.seeking_venue.data,
         seeking_description= form.seeking_description.data
         )
      db.session.add(new_artist)
      db.session.commit()
  # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    except:  
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred. Artist ' + form.name.data + ' could not be listed.') 
  
    finally:
       db.session.close()

  else: 
    flash('an error occurred. please try again') 
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).all()
  data = []
  for show in shows:
      data.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": str(show.start_time)  # Convert start_time to string if needed
        })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  if form.validate():
    try:
        new_show = Show(
        artist_id=form.artist_id.data,
        venue_id=form.venue_id.data,
        start_time=form.start_time.data
        )
        db.session.add(new_show)
        db.session.commit()
  # on successful db insert, flash success
        flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed', 'error')
    finally:
        db.session.close()
  else:
    flash('An error occurred. Please try again', 'error')  
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
