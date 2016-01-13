#!/usr/bin/python
#
# (c) 2015 descilla <mail@simon-wuellhorst.de>
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
import glob, os, json, collections, argparse


parser = argparse.ArgumentParser(description='This Script calculates the daily max user and node count by given nodes.json files.')
parser.add_argument('--filepath', required=True, help='location of nodes.json files')
parser.add_argument('--filepattern', required=True, help='filename pattern of node.json files e. g. "nodes_*"', default='*')
args = parser.parse_args()

class DailyMax:
	def __init__(self, directory, pattern ='*'):
		self.directory = directory
		self.pattern = pattern
		self.fileNames = []
		self.results = {}
		self.getFiles()
		self.calculateMax()
		self.printResults()
		
	def getFiles(self):
		for file in glob.iglob(self.directory+'/'+self.pattern):
			self.fileNames.append(file)

	def calculateMax(self):
		for file in self.fileNames:
			resource = open(file)
			try:
				data = json.loads(resource.read())
			except ValueError:
				print file, 'is broken'
			finally:
				resource.close()
			self.parseJson(data)

	def parseJson(self, data):
		nodes_online = 0
		users_online = 0
		day_stamp = data['timestamp'].split('T')[0]
		for node in data['nodes'].itervalues():
			if 'statistics' in node:
				users_online += node['statistics']['clients']
			if 'flags' in node:
				if node['flags']['online'] == True:
					nodes_online += 1
		if day_stamp in self.results:
			if self.results[day_stamp]['nodes_online'] < nodes_online:
				self.results[day_stamp]['nodes_online'] = nodes_online
			if self.results[day_stamp]['users_online'] < users_online:
				self.results[day_stamp]['users_online'] = users_online
		else:
			self.results[day_stamp] = {
				'nodes_online' : nodes_online,
				'users_online' : users_online
			}

	def printResults(self):
		ordered = collections.OrderedDict(sorted(self.results.items()))
		print "date\tnodes_online\tusers_online"
		for k,v in ordered.iteritems():
			print k+'\t'+str(v['nodes_online'])+'\t'+str(v['users_online'])

dmax = DailyMax(args.filepath, pattern = args.filepattern)