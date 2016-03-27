#!/usr/bin/python
# -*- coding: utf-8 -
#Imports:
import urllib
import json
from pprint import pprint
from node import Node
from geocode import Geocode

class Graph:
	def __init__(self, nodesData, graphData):
		self.coder = Geocode(geocoderCache = True, printStatus = True)
		self.data = graphData
		self.nodes = nodesData
		self.nodes_list = {}
		self.nodes_no_autoupdater = {}
		self.nodes_no_geo = {}
		self.parseNodes()
		self.parseLinks()
		self.calculateStepsToVpn()
		self.findMissingGeo()

	def parseNodes(self):
		for k,v in self.nodes['nodes'].iteritems():
			lat, lon = self.getGeo(k)
			node = Node(k, ipv6 = self.getPublicAddress(k), hostname = self.getHostname(k), isOnline = self.getOnlineState(k), lat=lat, lon=lon, coder = self.coder, autoupdater = self.getAutoupdaterStatus(k), branch = self.getBranch(k), isGateway = self.getIsGateway(k))
			self.nodes_list[k] = node

	def parseLinks(self):
		link_nodes = self.data['batadv']['nodes']
		for link in self.data['batadv']['links']:
			if 'node_id' in link_nodes[link['source']] and 'node_id' in link_nodes[link['target']]:#else it is a vpn link
				if self.nodes_list[link_nodes[link['source']]['node_id']].isGateway == True or self.nodes_list[link_nodes[link['target']]['node_id']].isGateway:
					self.setVpnLink(link['source'], link['target'])
				else:
					self.setLinkBetween(link_nodes[link['source']]['node_id'], link_nodes[link['target']]['node_id'])
			else:
				self.setVpnLink(link['source'], link['target'])
					
	def setLinkBetween(self, src, dst, stateOnline = True, lastSeen = None):
		if src and dst:
			self.nodes_list[src].links[dst] = {
				'node' : self.nodes_list[dst],
				'state_online' : stateOnline,
				'last_seen' : lastSeen
			}
			self.nodes_list[dst].links[src] = {
				'node' : self.nodes_list[src],
				'state_online' : stateOnline,
				'last_seen' : lastSeen
			}

	def setVpnLink(self, src, dst):
			if 'node_id' not in self.data['batadv']['nodes'][src] or (self.data['batadv']['nodes'][src]['node_id'] and self.nodes_list[self.data['batadv']['nodes'][src]['node_id']].isGateway == True):
				if 'node_id' in self.data['batadv']['nodes'][dst] and self.data['batadv']['nodes'][dst]['node_id']:
					self.nodes_list[self.data['batadv']['nodes'][dst]['node_id']].stepsToVpn = 0
			elif 'node_id' not in self.data['batadv']['nodes'][dst] or (self.data['batadv']['nodes'][dst]['node_id'] and self.nodes_list[self.data['batadv']['nodes'][dst]['node_id']].isGateway == True):
				if 'node_id' in self.data['batadv']['nodes'][src] and self.data['batadv']['nodes'][src]['node_id']:
					self.nodes_list[self.data['batadv']['nodes'][src]['node_id']].stepsToVpn = 0

	def calculateStepsToVpn(self):
		for node in self.nodes_list.itervalues():
			node.calculateStepsToVpn()

	def findMissingGeo(self):
		for node in self.nodes_list.itervalues():
			node.findMissingGeo()

	def getAllLevelXNodes(self, level, online = True):
		zmap = {}
		for k,v in self.nodes_list.iteritems():
			if v.isOnline or online == False:
				if v.stepsToVpn == level:
					zmap[k] = v
		return zmap


	def getHostname(self,node_id):
		return self.nodes['nodes'][node_id]['nodeinfo']['hostname']

	def getIsGateway(self,node_id):
		return self.nodes['nodes'][node_id]['flags']['gateway']

	def getAutoupdaterStatus(self, node_id):
		#return True
		if 'autoupdater' in self.nodes['nodes'][node_id]['nodeinfo']['software']:
			return self.nodes['nodes'][node_id]['nodeinfo']['software']['autoupdater']['enabled']
		else:
			#if node is offline for a long time sometimes no autoupdater status can be found
			return False

	def getBranch(self, node_id):
		#return True
		if 'autoupdater' in self.nodes['nodes'][node_id]['nodeinfo']['software']:
			return self.nodes['nodes'][node_id]['nodeinfo']['software']['autoupdater']['branch']
		else:
			#if node is offline for a long time sometimes no autoupdater status can be found
			return None

	def getGeo(self, node_id):
		if 'location' in self.nodes['nodes'][node_id]['nodeinfo'] and 'latitude' in self.nodes['nodes'][node_id]['nodeinfo']['location'] and 'longitude' in self.nodes['nodes'][node_id]['nodeinfo']['location']:
			return self.nodes['nodes'][node_id]['nodeinfo']['location']['latitude'], self.nodes['nodes'][node_id]['nodeinfo']['location']['longitude']
		return None, None

	def getPublicAddress(self,node_id):
		if node_id in self.nodes['nodes']:
			if 'addresses' in self.nodes['nodes'][node_id]['nodeinfo']['network']:
				for address in self.nodes['nodes'][node_id]['nodeinfo']['network']['addresses']:
					if address.startswith('2a03'):
						return address
		return None

	def getOnlineState(self,node_id):
		return self.nodes['nodes'][node_id]['flags']['online']


	def getNodeCloudsIn(self, region, branch = 'stable'):
		results = {}
		noAuto = False
		for k,v in self.getAllLevelXNodes(0).iteritems():
			if v.isOnline == True:
				if v.geodata != None:
					if v.isInRegion(region):
						noAuto = False
						for ksub,vsub in v.getNodeCloud({}).iteritems():
							if not vsub.autoupdater or (branch and vsub.branch != branch):
								#break
								noAuto = True
								self.nodes_no_autoupdater[ksub] = vsub
						#else:
						if not noAuto:
							results.update(v.getNodeCloud({}))
				else:
					self.nodes_no_geo.update(v.getNodeCloud({}))
		print "Result:",len(results), region
		return results

	def maxDepth(self):
		maxDepth = 0
		for v in self.nodes_list.itervalues():
			if v.stepsToVpn > maxDepth:
				maxDepth = v.stepsToVpn
		return maxDepth+1