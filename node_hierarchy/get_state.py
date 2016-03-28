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
import glob, os, json, collections, argparse, urllib

class OfflineChecker:
	def __init__(self, fileName):
		self.printStatus = True
		self.fileNames = []
		self.results = {}
		self.data = self.__getFile__(fileName)
		self.addresses = self.__getFile__('nodes_legacy_adresses.json')
		self.addressesOld = self.__getFile__('nodes_legacy_adresses_old.json')
		self.parseJson(self.data)
		self.getFwState()
		#self.printResults()
		
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

	def searchInLog(self, key, arg):
		files = ['/var/log/nginx/access.log', '/var/log/nginx/access.log.1']
		for fil in files:
			with open(fil) as lg:
				for line in lg:
					if key and key in line:
						if arg in line:
							date = line.split('[')[1].split(']')[0]
							dest_dom = line.split('gluon-')[1].split('-')[0]
							return date, dest_dom
		return None, None

	def parseJson(self, data):
		nodes_online = 0
		users_online = 0
		day_stamp = data['timestamp'].split('T')[0]
		for key, node in data['nodes'].iteritems():
			if 'statistics' in node:
				users_online += node['statistics']['clients']
			if 'flags' in node:
				if node['flags']['online'] == False:
					if 'system' in node['nodeinfo']:
						siteCode = node['nodeinfo']['system']['site_code']
						if siteCode not in self.results:
							self.results[siteCode] = {}
						self.results[siteCode][key] = {
							'lastseen' : node['lastseen'],
							'id' : key,
							'mac' : node['nodeinfo']['network']['mac'],
							'pub_v6' : self.getPublicAddress(node),
							'name' : node['nodeinfo']['hostname']
						}

	def getFwState(self):
		print 'fw_geladen\tlastseen\tziel_dom\tipv6_adresse\tnodeid\thostname\tmailaddress'
		for node, val in self.results['ffms'].iteritems():
			date, dest_dom = self.searchInLog(val['pub_v6'], "sysupgrade.bin")
			if date and dest_dom:
				#mail = self.addresses['nodes'][node]['nodeinfo']['owner']['contact'] if node in self.addresses['nodes'] and 'owner' in self.addresses['nodes'][node]['nodeinfo'] else ''
				mail = 'JA' if (node in self.addresses['nodes'] and 'owner' in self.addresses['nodes'][node]['nodeinfo']) or (node in self.addressesOld['nodes'] and 'owner' in self.addressesOld['nodes'][node]['nodeinfo']) else 'NEIN'
				print date +'\t'+ val['lastseen'] + '\t' + dest_dom + '\t' + val['pub_v6'] + '\t' + node + '\t' + val['name'] + '\t' + mail


	def printResults(self):
		ordered = collections.OrderedDict(sorted(self.results.items()))
		print "date\tnodes_online\tusers_online"
		for k,v in ordered.iteritems():
			print k+'\t'+str(v['nodes_online'])+'\t'+str(v['users_online'])


	def getPublicAddress(self,node):
		if 'addresses' in node['nodeinfo']['network']:
			for address in node['nodeinfo']['network']['addresses']:
				if address.startswith('2a03'):
					return address
		return None

dmax = OfflineChecker('http://karte.freifunk-muensterland.org/data/nodes.json')