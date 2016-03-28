#!/usr/bin/python
# -*- coding: utf-8 -
#Imports:
import argparse, json, sys
from domain_selector import DomainSelector
from hieraException import HieraException

parser = argparse.ArgumentParser(description='This Script generates a hierarchical nodes list for node migration using nginx geo feature.')
parser.add_argument('--json-path', required=False, default='https://service.freifunk-muensterland.de/maps/data/', help='Path of nodes.json and graph.json (can be local folder or remote URL).')
parser.add_argument('--targets-file', required=False, help='Json file of targets for nominatim geocoder.', default='./targets.json')
parser.add_argument('-t', '--targets', nargs='*', required=False, help='List of target names from target-file which should be proceeded. Example: -t citya -t cityb ...')
parser.add_argument('-a', '--all', '--all-targets', required=False, help='Proceed all targets from targets file.', action='store_true')
parser.add_argument('--out-path', required=False, help='Directory where the generated Output should stored.', default='./webserver-configuration/')
parser.add_argument('--only-specific-branch', required=False, help='Only attend nodes from specific branch.', default=None)
parser.add_argument('-p', '--print-status', required=False, action='store_true', help='Print Status (like geocoder tasks).')
args = parser.parse_args()

def prepareTargets(args):

	resource = open(args.targets_file)
	targets = json.loads(resource.read())
	resource.close()

	if len(targets) == 0:
		print "\033[91mError:\033[0m No targets were found in targets file."
		sys.exit(1)
	if args.all == True:
		return targets
	elif args.targets == None or len(args.targets) == 0:
		print "\033[91mError:\033[0m No target was given as argument and even --all switch was not enabled."
		sys.exit(1)
	else:
		specific_targets = {}
		for k, v in targets.iteritems():
			if k in args.targets:
				specific_targets[k] = v
		return specific_targets



print args

targets = prepareTargets(args)



#ds = DomainSelector(nodesFile = 'nodes.json', graphFile = 'graph.json', printStatus = True, dataPath = '../domaenensplit_webserver_config/', targets = targets)
#ds = DomainSelector(nodesFile = 'https://service.freifunk-muensterland.de/maps/data_legacy/nodes.json', graphFile = 'https://service.freifunk-muensterland.de/maps/data_legacy/graph.json', printStatus = True, dataPath = '../domaenensplit_webserver_config/', targets = targets, branch = None)
try:
	ds = DomainSelector(nodesFile = args.json_path.rstrip('/')+'/nodes.json', graphFile = args.json_path.rstrip('/')+'/graph.json', printStatus = args.print_status, dataPath = args.out_path, targets = targets, branch = args.only_specific_branch)
except HieraException:
	print "\033[93mFailed:\033[0m Process was interrupted by HieraException-Exception (see error messages above)."