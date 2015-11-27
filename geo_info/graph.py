#!/usr/bin/python
# -*- coding: utf-8 -
class Graph:
	def __init__(self, start_point = None):
		self.start_point = start_point
		self.points = {}
	
	def add_point(self, point_name):
		if not self.start_point:
			self.start_point = Point(point_name)
			self.points[point_name] = self.start_point
		else:
			self.points[point_name] = Point(point_name)

	def get_point(self, point_name):
		if point_name in self.points:
			return self.points[point_name]
		else:
			return None

	def set_root_point(self, point_name):
		if point_name in self.points:
			self.start_point = self.points[point_name]

	def add_edge_between(self, start_point, end_node, weight = 1):
		if start_point in self.points and end_node in self.points:
			self.points[start_point].add_edge(self.points[end_node], weight)

	def print_graph(self):
		print self.start_point.name
		self.__hiera_print__(self.start_point, 1)

	def __hiera_print__(self, point, indent):
		for edge in point.edges.itervalues():
			print ' '*indent*4+'Name: '+edge['point'].name+', Weight: '+str(edge['weight'])
			self.__hiera_print__(edge['point'], indent+1)


class Point:
	def __init__(self, name):
		self.name = name
		self.edges = {}

	def add_edge(self, neighbour_point, weight):
		self.edges[neighbour_point.name] = {
			'point' : neighbour_point,
			'weight' : weight
		}
	#def get_edges(self):
	#	return self.edge