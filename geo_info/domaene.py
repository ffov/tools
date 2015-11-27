#!/usr/bin/python
# -*- coding: utf-8 -
import urllib, json, datetime, time
from graph import Graph, Point
from geocode import Geocode

class Domaene:
	def __init__(self, nodes, printStatus = False):
		self.graph = Graph()
		self.nodes = nodes
		self.printStatus = printStatus
		self.coder = Geocode(geocoderCache = True, printStatus = printStatus)
		self.results = self.__init_results__()
		self.__get_geodata__()
		self.__init_graph__()
		self.count = 0

	def generate_hiera_list(self):
		for node in self.nodes:
			if 'geodata' in node:
				if node['geodata']:
					self.results['Gesamt']['count'] += 1
					self.__node_hiera__(node['geodata'], self.results['Gesamt']['childs'], self.graph.start_point, 'Gesamt')

	def __node_hiera__(self, geodata, result_layer, graph_layer, parent_name):
		# sometimes nominatim results are bad and no startpoint can be found
		if graph_layer.name not in geodata:
			return None
		geo_name = geodata[graph_layer.name]

		next_step = {
			'point' : None,
			'weight' : -1
		}
		for name, entry in self.graph.get_point(graph_layer.name).edges.iteritems():
			if name in geodata:
				if next_step['weight'] > entry['weight'] or next_step['weight'] == -1:
					next_step['point'] = entry['point']
					next_step['weight'] = entry['weight']

		if geo_name == parent_name:
			if next_step['point']:
				self.__node_hiera__(geodata, result_layer, next_step['point'],geo_name)
		else:
			
			if geo_name in result_layer:
				result_layer[geo_name]['count'] += 1
			else:
				result_layer[geo_name] = {
					'count' : 1,
					'childs' : {}
				}
			if next_step['point']:
				self.__node_hiera__(geodata, result_layer[geo_name]['childs'], next_step['point'],geo_name)

	def results_as_indent(self):
		if self.results:
			self.__hiera_as_indent__(self.results,0)
		else:
			print "No results generated"

	def __hiera_as_indent__(self, layer, indent):
		for k,v in layer.iteritems():
			print ' '*indent*4+k+': '+str(v['count'])
			if v['childs']:
				self.__hiera_as_indent__(v['childs'],indent+1)

	def results_as_dokuwiki_list(self):
		if self.results:
			self.__hiera_as_dokuwiki_list__(self.results,0)
		else:
			print "No results generated"

	def __hiera_as_dokuwiki_list__(self, layer, indent):
		for k,v in layer.iteritems():
			print '  '+' '*indent*2+'* '+k+': '+str(v['count'])
			if v['childs']:
				self.__hiera_as_dokuwiki_list__(v['childs'],indent+1)

	def __init_results__(self):
		return {
			'Gesamt' : {
				'count' : 0,
				'childs' : {}
			}
			
		}
	def __get_geodata__(self):
		for node in self.nodes:
			result = self.coder.getGeo(node['lon'], node['lat'])
			if result:
				node['geodata'] = result['payload']
				if result['cached'] == False:
	 				time.sleep(1)
	 		else:
	 			node['geodata'] = None

	def __init_graph__(self):
		self.graph.add_point('administrative')
		self.graph.add_point('hamlet')
		self.graph.add_point('residential')
		self.graph.add_point('village')
		self.graph.add_point('neighbourhood')
		self.graph.add_point('city')
		self.graph.add_point('city_district')
		self.graph.add_point('suburb')
		self.graph.add_point('town')
		self.graph.add_point('state_district')
		self.graph.add_point('county')
		self.graph.add_point('state')
		self.graph.add_point('country')

		self.graph.set_root_point('country')

		self.graph.add_edge_between('country', 'state')

		self.graph.add_edge_between('state','state_district', 1)
		self.graph.add_edge_between('state','county', 2)

		self.graph.add_edge_between('state_district','county')

		self.graph.add_edge_between('county', 'city', 1)
		self.graph.add_edge_between('county', 'town', 2)
		self.graph.add_edge_between('county', 'city_district', 3)#Häger issue if village is preferred over city_district
		self.graph.add_edge_between('county', 'village', 4)


		self.graph.add_edge_between('city', 'city_district')

		self.graph.add_edge_between('city_district', 'suburb', 1)
		self.graph.add_edge_between('city_district', 'residential', 2)

		self.graph.add_edge_between('town', 'city_district', 1)
		self.graph.add_edge_between('town', 'suburb', 2)
		self.graph.add_edge_between('town', 'residential',3)

		#self.graph.add_edge_between('village', 'city_district', 1)
		self.graph.add_edge_between('village', 'suburb', 2)
		self.graph.add_edge_between('village', 'residential',3)
		self.graph.add_edge_between('village', 'neighbourhood',4)

		self.graph.add_edge_between('suburb', 'hamlet', 1)
		self.graph.add_edge_between('suburb', 'neighbourhood', 2)
		self.graph.add_edge_between('suburb', 'administrative', 3)