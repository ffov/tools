#!/bin/env python
# -*- coding: utf-8 -*-
# neighbor.py
# Version 0.5.1
# by Michael Suelmann <suelmann@gmx.de>

from __future__ import print_function

# Configuration

ssh_node = 'root@freifunk'
map_url = 'https://freifunk-muensterland.de/map/data/nodes.json'
graph_url = 'https://freifunk-muensterland.de/map/data/graph.json'
max_distance = 75
max_processes = 0
use_status_page = False
use_batctl = False

import sys, os, re, json, subprocess, time, socket
from math import radians, cos, sin, asin, sqrt
from multiprocessing import Pool
try:
    from urllib2 import urlopen, URLError
except:
    from urllib.request import urlopen, URLError

FNULL = open(os.devnull, 'w')

def get_global_ip(ip_list):
    for ip in ip_list:
        if not re.match('fe80:', ip):
            return ip
    return ''

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    m = 6367000 * c
    return m

def distance(loc1, loc2):
    return haversine(loc1['longitude'],loc1['latitude'],loc2['longitude'],loc2['latitude'])

def get_hops(mac):
    try:
        output = subprocess.check_output(['ssh', ssh_node, 'batctl', 'tr', mac], stderr=FNULL)
    except subprocess.CalledProcessError as e:
        return -1
    hops = -1
    for line in re.split('\n',output):
        if re.match('\s*(\d+): \*', line): # output contains timeout
            return get_hops(mac)           # try again
        match = re.match('\s*(\d+): (\w\w:\w\w:\w\w:\w\w)', line)
        if match and match.group(2) != 'de:ad:be:ef':
            hops = hops + 1
    return hops

def get_hops_from_graph(node):
    if node in unconnected:
        return -1
    for i in range(len(hops_from_graph)):
        if node in hops_from_graph[i]:
            return i

def get_info(node):
    node_data = map_data['nodes'][node]['nodeinfo']
    dist = ''
    try:
        dist = distance(location,node_data['location'])
    except KeyError:
        pass
    if use_batctl:
        hops = get_hops(node_data['network']['mac'])
    else:
        hops = get_hops_from_graph(node)
    return (hops,
        node_data['hostname']+';'
        +node_data['network']['mac']+';'
        +get_global_ip(node_data['network']['addresses'])+';'
        +str(hops)+';'
        +str(dist)+';'
        +('Ja' if map_data['nodes'][node]['flags']['online'] else 'Nein'))

def add_connected(node):
    """
    Add all stations connected via mesh according to status page.
    Works recursively.
    """
    if not use_status_page:
        return
    #print('add_connected '+node)
    try:
        if not map_data['nodes'][node]['flags']['online']:
            return
        ip = get_global_ip(map_data['nodes'][node]['nodeinfo']['network']['addresses'])
        if not ip:
            return
    except KeyError:
        return
    try:
        status = urlopen('http://['+ip+']/cgi-bin/status', timeout=4)
        for line in status.readlines():
            match = re.match('Station .*(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)', line)
            if match:
                mac = match.group(1)
                try:
                    cnode = mac_nodes[mac]
                    if not cnode in nodes:
                        nodes.add(cnode)
                        add_links(cnode)
                        add_connected(cnode)
                        add_neighbors(cnode)
                except KeyError:
                    pass
    except (URLError, socket.timeout):
        print('Status page for node '+node+' not reachable', file=sys.stderr)

def add_neighbors(node):
    """
    Add all nodes nearby on the map.
    Works recursively.
    """
    #print('add_neighbors '+node)
    try:
        location = map_data['nodes'][node]['nodeinfo']['location']
    except KeyError:
        return
    for i in map_data['nodes'].keys():
        if not i in nodes:
            try:
                dist = distance(location, map_data['nodes'][i]['nodeinfo']['location'])
            except KeyError:
                dist = 999999
            if dist <=  max_distance:
                nodes.add(i)
                add_links(i)
                add_connected(i)
                add_neighbors(i)

def add_links(node):
    if node in links:
        for lnode in links[node]:
            if lnode != 'gw' and not lnode in nodes:
                nodes.add(lnode)
                add_links(lnode)
                add_connected(lnode)
                add_neighbors(lnode)

def add_to_links(node1, node2):
    if node1 in links:
        links[node1].append(node2)
    else:
        links[node1] = [node2]

# Main Start
if len(sys.argv) != 2:
    sys.exit('Usage: '+sys.argv[0]+' <IPV6 address|MAC address>')

# Get web data
response = urlopen(map_url)
map_data = json.loads(response.read())
response = urlopen(graph_url)
graph_data = json.loads(response.read())['batadv']

# transform links into better datastructure
nodes = graph_data['nodes']
links = dict()
gw = re.compile('de:ad:be:ef')
for link in graph_data['links']:
    if gw.match(nodes[link['source']]['id']) and 'node_id' in nodes[link['target']]:
        add_to_links(nodes[link['target']]['node_id'],'gw')
    elif gw.match(nodes[link['target']]['id']) and 'node_id' in nodes[link['source']]:
        add_to_links(nodes[link['source']]['node_id'],'gw')
    elif 'node_id' in nodes[link['source']] and 'node_id' in nodes[link['target']]:
        add_to_links(nodes[link['target']]['node_id'],nodes[link['source']]['node_id'])
        add_to_links(nodes[link['source']]['node_id'],nodes[link['target']]['node_id'])

# get starting node from command line parameter
node = ''
if re.match('\w\w:\w\w:\w\w:\w\w:\w\w:\w\w$', sys.argv[1]):
    try:
        node = sys.argv[1].replace(':', '')
        ip = get_global_ip(map_data['nodes'][node]['nodeinfo']['network']['addresses'])
    except KeyError:
        sys.exit('Node with MAC address '+sys.argv[1]+' not found.')
else:
    ip = sys.argv[1]
    for i in map_data['nodes'].keys():
        try:
            if get_global_ip(map_data['nodes'][i]['nodeinfo']['network']['addresses']) == ip:
                node = i
        except KeyError:
            pass
    if node == '':
        sys.exit('Node with IP address '+ip+' not found.')

# build dict of nodes for macs in mesh interfaces for add_connected()
mac_nodes = dict()
for i in map_data['nodes'].keys():
    try:
        for mac in map_data['nodes'][i]['nodeinfo']['network']['mesh_interfaces']:
            mac_nodes[mac] = i
    except KeyError:
        pass

# process starting node which adds neighbors recursively
try:
    location = map_data['nodes'][node]['nodeinfo']['location']
except KeyError:
    sys.exit('No location data available for node '+node)
nodes = set()
nodes.add(node)
add_links(node)
add_neighbors(node)
add_connected(node)

# calculate hop count from links
hops_from_graph = [set()]
unconnected = set()
for node in nodes:
    if node in links and 'gw' in links[node]:
        hops_from_graph[0].add(node)
    else:
        unconnected.add(node)
count = 1
while len(unconnected) > 0:
    found_one = False
    hops_from_graph.append(set())
    for node in unconnected:
        if node in links:
            for lnode in links[node]:
                if lnode in hops_from_graph[count-1]:
                    hops_from_graph[count].add(node)
                    found_one = True
    if not found_one:
        break
    unconnected = unconnected - hops_from_graph[count]
    count = count+1

# assemble info for all nodes found
if max_processes > 0:
    p = Pool(max_processes)
    info = p.map(get_info, nodes)
else:
    info = map(get_info, nodes)

# produce output
info.sort(key=lambda x: -x[0])
f = open(time.strftime('%Y-%m-%d_%H-%M-%S')+'_'+node+'.txt', 'w')
print('Name;MAC;IP;Hops;Distance;Online',file=f)
hops = 99
for line in info:
    if line[0] < hops:
        hops = line[0]
        if hops == -1:
            text = 'Nicht erreichbar'
        elif hops == 0:
            text = 'VPN'
        elif hops == 1:
            text = '1 Sprung'
        else:
            text = str(hops)+' Sprünge'
        print(text+':')
        print(text+':', file=f)
    print(line[1])
    print(line[1].encode('utf8'), file=f)
