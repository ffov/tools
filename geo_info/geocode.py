#!/usr/bin/python
# -*- coding: utf-8 -
#import time
from geopy.geocoders import Nominatim
from blitzdb import Document, FileBackend
class GeoAssign(Document):
	pass
class Geocode:
	def __init__(self, geocoderCache = True, printStatus = False):
		self.printStatus = printStatus
		self.geocoderCache = geocoderCache
		if self.geocoderCache:
			self.db = FileBackend('./geo-cache')
	def getGeo(self, lon, lat):
		if self.geocoderCache:
			try:
				nodeObj = self.db.get(GeoAssign,{'lat' : lat, 'lon' : lon})
				nodeObj['cached'] = True
				return nodeObj
			except GeoAssign.DoesNotExist:
				pass
		if self.printStatus:
			print('lon: '+str(lon)+', lat: '+str(lat)+' not in cache - start lookup at Nominatim-API')
		geolocator = Nominatim()
		location = geolocator.reverse([lat, lon], timeout=20)
		if 'address' in location.raw:
			location = location.raw['address']
			nodeObj = GeoAssign({
				'lat' : lat,
				'lon' : lon,
				'payload' : location
				})
			self.db.save(nodeObj)
			self.db.commit()
			nodeObj['cached'] = False
			return nodeObj
		else:
			# got no results (i.e. coordinates are incorrect)
			return None