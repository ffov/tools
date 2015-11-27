#!/usr/bin/python
# -*- coding: utf-8 -
#Imports:
from nodesParser import NodesParser
from domaene import Domaene

nodefile = 'http://ffms-map.fungur.eu/data/nodes.json'
#nodefile = "https://freifunk-muensterland.de/map/data/nodes.json"
#nodefile = 'nodes.json'

nodes_parser = NodesParser('ffms', nodefile, printStatus = True)
nodes = nodes_parser.getGeoNodes(isOnline = True, lastSeenHours = 24)

domaene = Domaene(nodes, printStatus = True)
domaene.generate_hiera_list()
#domaene.results_as_indent()
domaene.results_as_dokuwiki_list()