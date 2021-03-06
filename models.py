from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

import urllib
import geocoder
import json

db = SQLAlchemy()

class User(db.Model):
	__tablename__='users'
	uid=db.Column(db.Integer, primary_key=True)
	firstname=db.Column(db.String(50))
	lastname=db.Column(db.String(50))
	email=db.Column(db.String(100), unique=True)
	pwdhash=db.Column(db.String(54))

	def __init__(self, firstname, lastname, email, password):
		self.firstname=firstname.title()
		self.lastname=lastname.title()
		self.email=email.lower()
		self.set_password(password)

	def set_password(self, password):
		self.pwdhash=generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.pwdhash, password)


class Place(object):
  def meters_to_walking_time(self, meters):
    # 80 meters is one minute walking time
    return int(meters / 80)  

  def wiki_path(self, s):
    return urllib.parse.urljoin("http://en.wikipedia.org/wiki/", s.replace(' ', '_'))
  
  def address_to_latlng(self, address):
    g = geocoder.google(address)
    return (g.lat, g.lng)

  def query(self, address):
    lat, lng = self.address_to_latlng(address)
    
    query_url = 'https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gsradius=5000&gscoord={0}%7C{1}&gslimit=8&format=json'.format(lat, lng)
    d = urllib.request.urlopen(query_url)
    json_data = d.read()
    d.close()

    data = json.loads(json_data)
    
    places = []
    for place in data['query']['geosearch']:
      place_name = place['title']
      meters = place['dist']
      lat = place['lat']
      lng = place['lon']

      wiki_url = self.wiki_path(place_name)
      walking_time = self.meters_to_walking_time(meters)

      place_dict = {
        'name': place_name,
        'url': wiki_url,
        'time': walking_time,
        'lat': lat,
        'lng': lng
      }

      places.append(place_dict)

    return places