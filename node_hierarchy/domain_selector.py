#!/usr/bin/python
# -*- coding: utf-8 -
#Imports:
import json, urllib, os, glob
from graph import Graph
from hieraException import HieraException

class DomainSelector:
	def __init__(self, nodesFile, graphFile, dataPath = './', printStatus = False, targets = None, branch = 'stable'):
		if not os.path.isdir(dataPath):
			print "\033[91mError:\033[0m Output folder was not found or is not writable. Given path:", dataPath
			raise HieraException

		self.printStatus = printStatus
		self.targets = targets
		self.dataPath = dataPath.rstrip('/')
		self.nodesData = self.__getFile__(nodesFile)
		self.graphData = self.__getFile__(graphFile)

		self.__prepareOutDir__()

		self.graph = Graph(self.nodesData, self.graphData)
		if self.targets == None:
			self.writeConfigFiles(self.graph.nodes_list,"all")
			self.writeDumpFile(self.graph.nodes_list,"all")
		else:
			nodes = {}
			for k,v in self.targets.iteritems():
				nodes = self.graph.getNodeCloudsIn(v,branch)
				self.writeConfigFiles(nodes,k)
				self.writeDumpFile(nodes,k)
				nodes = {}
		self.writeConfigFiles(self.graph.getProblemNodes(noAutoupdater = True),"no_autoupdater")
		self.writeConfigFiles(self.graph.getProblemNodes(noGeodata = True),"no_geo")
		self.writeConfigFiles(self.graph.getProblemNodes(noGeodata = True, noAutoupdater = True),"no_nothing")

	def __prepareOutDir__(self):
		files = glob.glob(self.dataPath+'/*')
		for f in files:
		    os.remove(f)

	def __getFile__(self, nodesFile):
		if nodesFile.startswith('https://') or nodesFile.startswith('http://'):
			if self.printStatus:
				print 'Download', nodesFile.rsplit('/', 1)[1] , 'from URL:', nodesFile
			resource = urllib.urlopen(nodesFile)
		else:
			if self.printStatus:
				print 'Open', nodesFile.rsplit('/', 1)[1] , 'from file:', nodesFile
			resource = open(nodesFile)
		try:
			data = json.loads(resource.read())
		except:
			print "\033[91mError:\033[0m Error while parsing a json file (perhapes misformed file): ", nodesFile
			raise HieraException
		finally:
			resource.close()

		return data

	def writeConfigFiles(self, nodes, name):
		maxDepth = self.maxDepth(nodes)
		if len(nodes) > 0:
			for i in range(0,maxDepth):
				content = 'geo $switch {\n  default 0;'
				f = open(self.dataPath.rstrip('/')+'/'+name+'_node_level'+str(i),'w')
				for node in nodes.itervalues():
					if node.stepsToVpn == i:
						if node.ipv6 and node.hostname:
							content += '\n  '+node.ipv6+' 1; #'+node.hostname
				content += '\n}'
				f.write(content.encode('utf8'))
				f.close()

	def writeDumpFile(self, nodes, name):
		content = {}
		for node in nodes.itervalues():
			if node.ipv6 and node.hostname:
				content[node.nodeid] = {
					'nodeid' : node.nodeid,
					'ipv6' : node.ipv6,
					'hostname' : node.hostname,
					'level' : node.stepsToVpn,
				}
		with open(self.dataPath+'/'+name+'_node_statistics.json', 'w') as outfile:
			json.dump(content, outfile)

	def maxDepth(self, nodes):
		maxDepth = 0
		for v in nodes.itervalues():
			if v.stepsToVpn > maxDepth:
				maxDepth = v.stepsToVpn
		return maxDepth+1
