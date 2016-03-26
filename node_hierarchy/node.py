#!/usr/bin/python
# -*- coding: utf-8 -
from geocode import Geocode
import time

class Node(object):
	def __init__(self, nodeid, ipv6 = None, hostname = None, isOnline = False, lastSeen = None, lat = None, lon = None, coder = None, autoupdater = False, branch = None, isGateway = False):
		self.coder = coder
		if self.coder == None:
			self.coder = Geocode(geocoderCache = True, printStatus = True)
		self.links = {}
		self.nodeid = nodeid
		self.ipv6 = ipv6
		self.hostname = hostname
		self.stepsToVpn = -1
		self.isOnline = isOnline
		self.lastSeen = lastSeen
		self.autoupdater = autoupdater
		self.branch = branch
		self._geo = None
		self.geodata = None
		self.isGateway = isGateway
		if lat != None and lon != None:
			self.geo = {
				'lat' : lat,
				'lon' : lon
			}
		

	def addLink(self,nodeid, node):
		if not nodeid in self.links:
			self.links[nodeid] = node
		else:
			print "link still exists"

	def calculateStepsToVpn(self, trace = []):
		if self.stepsToVpn != 0:#self.stepsToVpn == -1 doesn't work, cause the shortest path could be the path to a former trace member
			own_trace = trace[:]#clone - trace for preventing loops in pathfinding in graph
			own_trace.append(self.nodeid)
			lowest = -1
			current = -1
			for k,v in self.links.iteritems():
				if k not in own_trace:
					current = v['node'].calculateStepsToVpn(own_trace)
					if lowest == -1 or current < lowest:
						lowest = current
			if lowest > -1:
				self.stepsToVpn = lowest+1
		return self.stepsToVpn

	def findMissingGeo(self, trace = []):
		if self.geo == None:
			own_trace = trace[:]
			own_trace.append(self.nodeid)
			geo = None
			for k,v in self.links.iteritems():
				if k not in own_trace:
					geo = v['node'].findMissingGeo(own_trace)
					if geo != None:
						self.geo = geo.copy()
						break
			return geo
		else:
			return self.geo

	def getNodeCloud(self, nodes = {}):
		nodes[self.nodeid] = self
		for k,v in self.links.iteritems():
			if k not in nodes:
				nodes = v['node'].getNodeCloud(nodes)
		return nodes

	def isInRegion(self, regions):
		#AND and OR Conditions are possible
		val = False
		if self.geodata == None:
			return False

		for region in regions:
			val = False
			for k,v in region.iteritems():
				if k in self.geodata and self.geodata[k] == v:
					val = True
				else:
					val = False
			if val:
				return True
		return val


	@property
	def geo(self):
		return self._geo

	@geo.setter
	def geo(self, value):
		self._geo = value
		self.__get_geodata__()

	def __get_geodata__(self):
		if self.geo != None:
			result = self.coder.getGeo(self.geo['lon'], self.geo['lat'])
			if result:
				self.geodata = result['payload']
				if result['cached'] == False:
					time.sleep(1)
			else:
				self['geodata'] = None