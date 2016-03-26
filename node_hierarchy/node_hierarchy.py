#!/usr/bin/python
# -*- coding: utf-8 -
#Imports:
from domain_selector import DomainSelector

targets = {
#	'muenster' : [
#		{'city' : u'Münster'}, 
#		{'county' : u'Münster'},
#	],
	# 'kreis_warendorf' : [
	# 	{'county' : u'Kreis Warendorf'},
	# ],
	# 'kreis_coesfeld' : [
	# 	{'county' : u'Kreis Coesfeld'},
	# ],
	# 'kreis_steinfurt_west' : [
	# 	{'town' : u'48565'},
	# 	{'village' : u'Wettringen'},
	# 	{'town' : u'Ochtrup'},
	# 	{'village' : u'Metelen'},
	# 	{'town' : u'Horstmar'},
	# 	{'village' : u'Laer'},
	# 	{'village' : u'Nordwalde'},
	# 	{'village' : u'Altenberge'},
	# ],
	# 'kreis_steinfurt_ost' : [
	# 	{'town' : u'Emsdetten'},
	# 	{'town' : u'Neuenkirchen'},
	# 	{'town' : u'Rheine'},
	# 	{'town' : u'Greven'},
	# 	{'village' : u'Ladbergen'},
	# 	{'town' : u'Lengerich'},
	# 	{'town' : u'Tecklenburg'},
	# 	{'village' : u'Lienen'},
	# ],
	# 'muenster_stadt' : [
	# 	{'city_district' : u'Münster-Mitte'},
	# 	{'city_district' : u'Münster-Nord'},
	# 	{'city_district' : u'Münster-Ost'},
	# 	{'suburb' : u'Berg Fidel'},
	# 	{'suburb' : u'Gremmendorf'},
	# 	{'suburb' : u'Mecklenbeck'},
	# 	{'suburb' : u'Gievenbeck'},
	# 	{'suburb' : u'Nienberge'},
	# 	{'suburb' : u'Roxel'},
	# 	{'suburb' : u'Sentruper Höhe'},
	# ],
	# 'muenster_sued' : [
	# 	{'suburb' : u'Amelsbüren'},
	# 	{'suburb' : u'Hiltrup'},
	# 	{'suburb' : u'Albachten'},
	# ],
	# 'kreis_borken' : [
	# 	{'town' : u'Ahaus'},
	# 	{'town' : u'Bocholt'},
	# 	{'town' : u'Borken'},
	# 	{'town' : u'Gescher'},
	# 	{'village' : u'Heek'},
	# 	{'town' : u'Heiden'},
	# 	{'town' : u'Isselburg'},
	# 	{'village' : u'Legden'},
	# 	{'town' : u'Raesfeld'},
	# 	{'town' : u'Reken'},
	# 	{'town' : u'Rhede'},
	# 	{'village' : u'Schöppingen'},
	# 	{'town' : u'Stadtlohn'},
	# 	{'village' : u'Südlohn'},
	# 	{'town' : u'Velen'},
	# 	{'town' : u'Vreden'},
	# ],
	# 'sassenberg' : [
	# 	{'town' : u'Sassenberg'},
	# ],
	# 'telgte' : [
	# 	{'town' : u'Telgte'},
	# ],
	# 'warendorf_stadt' : [
	# 	{'town' : u'Warendorf'},
	# ]
	'stadt_stadtlohn' : [
		{'town' : u'Stadtlohn'},
	],
	'stadt_bocholt' : [
		{'town' : u'Bocholt'},
	],
	'stadt_telgte' : [
		{'town' : u'Telgte'},
	],
	'stadt_warendorf' : [
		{'town' : u'Warendorf'},
	],
}

#ds = DomainSelector(nodesFile = 'nodes.json', graphFile = 'graph.json', printStatus = True, dataPath = '../domaenensplit_webserver_config/', targets = targets)
#ds = DomainSelector(nodesFile = 'https://service.freifunk-muensterland.de/maps/data_legacy/nodes.json', graphFile = 'https://service.freifunk-muensterland.de/maps/data_legacy/graph.json', printStatus = True, dataPath = '../domaenensplit_webserver_config/', targets = targets, branch = None)
ds = DomainSelector(nodesFile = 'https://service.freifunk-muensterland.de/maps/data/nodes.json', graphFile = 'https://service.freifunk-muensterland.de/maps/data/graph.json', printStatus = True, dataPath = '../domaenensplit_webserver_config/', targets = targets, branch = None)
