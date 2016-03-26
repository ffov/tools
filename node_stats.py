#!/usr/bin/python
# -*- coding: utf-8 -
#Imports:
import urllib, json, datetime, time

def getFile(nodesFile):
	printStatus = False
	if nodesFile.startswith('https://') or nodesFile.startswith('http://'):
		if printStatus:
			print "Download node.json from URL: " + nodesFile
		response = urllib.urlopen(nodesFile)
	else:
		if printStatus:
			print "Open node.json file: " + nodesFile
		response = open(nodesFile)
	return json.loads(response.read())

def getGeoNodes(data, lastSeenHours = False, isOnline = True):
	nodes = []
	count = 0
	lastDay = datetime.datetime.today() - datetime.timedelta(hours = lastSeenHours)
	for node in data['nodes'].itervalues():
		knoten = node['nodeinfo']
	 	if isOnline:
		 	if lastSeenHours != False and lastSeenHours != 0:
		 		if 'lastseen' in node:
			 		nodeLastSeen = datetime.datetime.strptime(node['lastseen'],'%Y-%m-%dT%H:%M:%S')
			 		if nodeLastSeen >= lastDay or node['flags']['online']:
			 			count += 1
		 	else:
			 	if node['flags']['online']:
			 		count += 1
		else:
			count += 1

	return count

nodefile = 'https://service.freifunk-muensterland.de/maps/data/nodes.json'
nodesData = getFile(nodefile)
print 'offset_days;nodes_count'
#for i in range(0,3648,24):
for i in range(0,4600,24):
	print str(i/24) + ';' + str(getGeoNodes(nodesData, i))
	#print 'Nodes online last ' + str(i/24) + ' days: ' + str(getGeoNodes(nodesData, i))
