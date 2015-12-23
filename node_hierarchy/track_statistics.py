#!/usr/bin/python
# -*- coding: utf-8 -
#Imports:
import json, urllib
import operator

class TrackStatistics:
	def __init__(self,nodesFile,statisticsFiles, printStatus = False):
		self.printStatus = printStatus
		self.nodesData = self.__getFile__(nodesFile)
		self.statisticsData = []
		for entry in statisticsFiles:
			self.statisticsData.append({'data' : self.__getFile__(entry['data']), 'name' : entry['name']})
		#print self.statisticsData
		for domain in self.statisticsData:
			self.printDomainStatisticsPerLevel(domain['data'], domain['name'])

	def printDomainStatisticsPerLevel(self,data, name = "not set"):
		#firmwareVersion = {}
		print '-'*50
		print 'Printing statistics for domain:', name
		for level in range(0,self.maxDepth(data)):
			firmwareVersion = {}
			for nodeid, node in data.iteritems():
				if level == node['level']:
					fwver = self.nodesData['nodes'][nodeid]['nodeinfo']['software']['firmware']['release']
					if fwver in firmwareVersion:
						firmwareVersion[fwver] += 1
					else:
						firmwareVersion[fwver] = 1
			print '\tLevel:',level
			for k,v in sorted(firmwareVersion.items(), key=operator.itemgetter(1), reverse = True):
				print '\t\t '+k+':\t'+str(v)
		print '-'*50
			



	def maxDepth(self, nodes):
		maxDepth = 0
		for v in nodes.itervalues():
			if v['level'] > maxDepth:
				maxDepth = v['level']
		return maxDepth+1

	def __getFile__(self, nodesFile):
		if nodesFile.startswith('https://') or nodesFile.startswith('http://'):
			if self.printStatus:
				print "Download node.json from URL: " + nodesFile
			resource = urllib.urlopen(nodesFile)
		else:
			if self.printStatus:
				print "Open node.json file: " + nodesFile
			resource = open(nodesFile)
		data = json.loads(resource.read())
		resource.close()
		return data

data = [
	{
		'data' : '../domaenensplit_webserver_config/muenster_sued_node_statistics.json',
		'name' : 'Münster Süd'
	},
	{
		'data' : '../domaenensplit_webserver_config/muenster_stadt_node_statistics.json',
		'name' : 'Münster Stadt'
	},
	{
		'data' : '../domaenensplit_webserver_config/kreis_coesfeld_node_statistics.json',
		'name' : 'Kreis Coesfeld'
	},
	{
		'data' : '../domaenensplit_webserver_config/kreis_warendorf_node_statistics.json',
		'name' : 'Kreis Warendorf'
	},
	{
		'data' : '../domaenensplit_webserver_config/kreis_steinfurt_ost_node_statistics.json',
		'name' : 'Kreis Steinfurt Ost'
	},
	{
		'data' : '../domaenensplit_webserver_config/kreis_steinfurt_west_node_statistics.json',
		'name' : 'Kreis Steinfurt West'
	},
	{
		'data' : '../domaenensplit_webserver_config/kreis_borken_node_statistics.json',
		'name' : 'Kreis Borken'
	},
]

#stat = TrackStatistics('nodes.json', data, printStatus = True)
stat = TrackStatistics('https://freifunk-muensterland.de/map/data/nodes.json', data, printStatus = True)