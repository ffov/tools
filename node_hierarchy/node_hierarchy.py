#!/usr/bin/python
# -*- coding: utf-8 -
#Imports:
import json
from graph import Graph

class NodeHierarchy:
	def __init__(self, nodesFile, graphFile, dataPath = './', printStatus = False, targets = None):
		self.printStatus = printStatus
		self.targets = targets
		self.nodesData = self.__getFile__(nodesFile)
		self.graphData = self.__getFile__(graphFile)
		self.dataPath = dataPath

		self.graph = Graph(self.nodesData, self.graphData)
		if self.targets == None:
			self.writeConfigFiles(self.graph.nodes_list,"all")
		else:
			nodes = {}
			for k,v in self.targets.iteritems():
				nodes = self.graph.getNodeCloudsIn(v)
				self.writeConfigFiles(nodes,k)
				nodes = {}

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

	def writeConfigFiles(self,nodes_level, name):
		maxDepth = self.maxDepth(nodes_level)
		for i in range(0,maxDepth):
			content = 'geo $switch {\n\tdefault\t0;'
			f = open(self.dataPath+'/'+name+'_node_level'+str(i),'w')
			for node in nodes_level.itervalues():
				if node.stepsToVpn == i:
					if node.ipv6 and node.hostname:
						content += '\n\t'+node.ipv6+'\t1;\t #'+node.hostname
					#else:
					#	print node.nodeid
			content += '\n}'
			f.write(content.encode('utf8'))
			f.close()

	def maxDepth(self, nodes):
		maxDepth = 0
		for v in nodes.itervalues():
			if v.stepsToVpn > maxDepth:
				maxDepth = v.stepsToVpn
		return maxDepth+1


targets = {
	'muenster' : [
		{'city' : u'Münster'}, 
		{'county' : u'Münster'}
	],
	'kreis_warendorf' : [
		{'county' : u'Kreis Warendorf'}
	],
	'kreis_coesfeld' : [
		{'county' : u'Kreis Coesfeld'}
	],
	'kreis_steinfurt_west' : [
		{'town' : u'48565'},
		{'village' : u'Wettringen'},
		{'town' : u'Ochtrup'},
		{'village' : u'Metelen'},
		{'town' : u'Horstmar'},
		{'village' : u'Laer'},
		{'village' : u'Nordwalde'},
		{'village' : u'Altenberge'}
	],
	'kreis_steinfurt_ost' : [
		{'town' : u'Emsdetten'},
		{'town' : u'Neuenkirchen'},
		{'town' : u'Rheine'},
		{'town' : u'Greven'},
		{'village' : u'Ladbergen'},
		{'town' : u'Lengerich'},
		{'town' : u'Tecklenburg'},
		{'village' : u'Lienen'},
	]
}

ds = NodeHierarchy(nodesFile = 'nodes.json', graphFile = 'graph.json', printStatus = True, dataPath = './results/', targets = targets)