#!/usr/bin/python
#
# (c) 2016 descilla <mail@simon-wuellhorst.de>
#
# This script is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License or any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License
# see <http://www.gnu.org/licenses/>.
#
import glob, os, json, collections, argparse, urllib, datetime
from collections import OrderedDict

class OfflineChecker:
	def __init__(self, dataFile):
		self.printStatus = False
		self.dataSet = self.__getFile__(dataFile)
		self.fileNames = []
		self.results = {}
		self.addresses = []
		self.getAddressFiles()
		self.getFwState()
		
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

	def getAddressFiles(self):
		for file in glob.iglob('./nodes_adresses_*'):
			self.addresses.append(self.__getFile__(file))

	def readFile(self):
		fil = 'operate.txt'
		results = []
		with open(fil) as lg:
			for line in lg:
				results.append(line)
		return results

	def getNodeAddressItem(self,ipv6):
		pub = ""
		i = 0
		for adr in self.addresses:
			i +=1
			for val in adr['nodes'].itervalues():
				pub = self.getPublicAddress(val)
				if pub and pub in ipv6:
					if 'owner' in val['nodeinfo']:
						return val

	def getNodeItem(self,ipv6):
		pub = ""
		for val in self.dataSet['nodes'].itervalues():
			pub = self.getPublicAddress(val)
			if pub and pub in ipv6:
				return val

	def getFwState(self):
		lastDay = datetime.datetime.today() - datetime.timedelta(hours = 48)
		onlyoldernodes = False
		results = {}
		for nodeIP in self.readFile():
			nodeAddresses = self.getNodeAddressItem(nodeIP)
			node = self.getNodeItem(nodeIP)
			if node:
				nodeLastSeen = datetime.datetime.strptime(node['lastseen'],'%Y-%m-%dT%H:%M:%S')
				if nodeLastSeen < lastDay or onlyoldernodes == False:
					au = node['nodeinfo']['software']['autoupdater']['branch']
					loca = 'JA' if 'location' in node['nodeinfo'] else 'NEIN'
					if nodeAddresses:
						mail = nodeAddresses['nodeinfo']['owner']['contact'] if 'owner' in nodeAddresses['nodeinfo'] else 'NEIN'
						#mail = 'JA' if 'owner' in nodeAddresses['nodeinfo'] else 'NEIN'
					else:
						mail = 'NEIN'
					results[node['nodeinfo']['node_id']] = {
						'lastseen' : node['lastseen'],
						'ipv6' : self.getPublicAddress(node),
						'node_id' : node['nodeinfo']['node_id'],
						'name' : node['nodeinfo']['hostname'],
						'contact' : mail,
						'fw_base' : node['nodeinfo']['software']['firmware']['base'],
						'fw_release' : node['nodeinfo']['software']['firmware']['release'],
						'au_enabled' : str(node['nodeinfo']['software']['autoupdater']['enabled']),
						'au_branch' : au,
						'router_modell' : node['nodeinfo']['hardware']['model'],
						'geo' : loca,
					}
					#print node['lastseen'] + ';' + self.getPublicAddress(node) + ';' + node['nodeinfo']['node_id'] + ';' + node['nodeinfo']['hostname'] + ';' + mail + ';' + node['nodeinfo']['software']['firmware']['base'] + ';' + node['nodeinfo']['software']['firmware']['release'] + ';' + str(node['nodeinfo']['software']['autoupdater']['enabled']) + ';' + au + ';' + node['nodeinfo']['hardware']['model'] + ';' + loca
		self.printCSV(results)
	def printCSV(self, data):
		od = OrderedDict(sorted(data.items(), key=lambda x: x[1]['lastseen'], reverse=True))
		print 'zuletzt online;nodeid;Knotenname;mailaddress;Firmware Base;Firmware Release;Autoupdater;AU-Branch;Router-Modell;geo'
		for item in od.itervalues():
			print item['lastseen'] + ';' + item['node_id'] + ';' + item['name'] + ';' + item['contact'] + ';' + item['fw_base'] + ';' + item['fw_release'] + ';' + item['au_enabled'] + ';' + item['au_branch'] + ';' + item['router_modell'] + ';' + item['geo']
	def getPublicAddress(self,node):
		if 'addresses' in node['nodeinfo']['network']:
			for address in node['nodeinfo']['network']['addresses']:
				if address.startswith('2a03'):
					return address
		return None

dmax = OfflineChecker('https://service.freifunk-muensterland.de/maps/data/nodes.json')