#!/usr/bin/python
# -*- coding: utf-8 -
import urllib, json, datetime, time
class NodesParser:
	def __init__(self, name, nodesFile, printStatus = False):
		self.name = name
		self.printStatus = printStatus
		self.__getFile__(nodesFile)

	def __getFile__(self, nodesFile):
		if nodesFile.startswith('https://') or nodesFile.startswith('http://'):
			if self.printStatus:
				print "Download node.json from URL: " + nodesFile
			response = urllib.urlopen(nodesFile)
		else:
			if self.printStatus:
				print "Open node.json file: " + nodesFile
			response = open(nodesFile)
		self.data = data = json.loads(response.read())

	def getGeoNodes(self, lastSeenHours = False, isOnline = True):
		nodes = []
		lastDay = datetime.datetime.today() - datetime.timedelta(hours = lastSeenHours)
		for node in self.data['nodes'].itervalues():
			knoten = node['nodeinfo']
		 	addNode = False
		 	if isOnline:
			 	if lastSeenHours != False and lastSeenHours != 0:
			 		if 'lastseen' in node:
				 		nodeLastSeen = datetime.datetime.strptime(node['lastseen'],'%Y-%m-%dT%H:%M:%S')
				 		if nodeLastSeen >= lastDay or node['flags']['online']:
				 			addNode = True
			 	else:
				 	if node['flags']['online']:
				 		addNode = True
			else:
				addNode = True

		 	if 'location' in knoten.keys():
		 		if addNode:
					nodes.append({
						'lon' : knoten['location']['longitude'],
						'lat' : knoten['location']['latitude'],
						'name' : knoten['hostname']
						})
		return nodes