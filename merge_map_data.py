#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# neighbor.py
# by Michael Suelmann <suelmann@gmx.de>

# Python3-Skript zum Zusammenfügen von Kartendaten verschiedener Freifunk-
# Domänen.

# Aufruf: merge_map_data.py -o Zielverzeichnis Quellverzeichnis1 ... QuellverzeichnisN


import sys, os, json, argparse

class Merger:
    def __init__(self):
        self.nodes = False
        self.graph = False

    def parse_args(self, argv):
        parser = argparse.ArgumentParser(description='Skript zum Zusammenfügen von Kartendaten verschiedener Freifunk-Domänen')
        parser.add_argument('-o', default=".", dest='output', type=str, help='Ausgabe-Verzeichnis')
        parser.add_argument('input', nargs='+', type=str, help='Eingabe-Verzeichnisse')
        self.args = parser.parse_args()

    def merge_nodes(self):
        for dir in self.args.input:
            try:
                file = open(dir+"/nodes.json","r")
            except:
                print('Could not open '+dir+"/nodes.json")
                continue
            nodes = json.load(file)
            if not nodes:
                continue
            for node in nodes['nodes']:
                if 'nodeinfo' in node and 'owner' in node['nodeinfo']:
                    del node['nodeinfo']['owner']
            if self.nodes:
                for node in nodes['nodes'].keys():
                    try:
                        if self.nodes['nodes'][node]['flags']['online']:
                            continue
                    except KeyError:
                        pass
                    self.nodes['nodes'][node] = nodes['nodes'][node]
                #self.nodes['nodes'].update(nodes['nodes'])
            else:
                self.nodes = nodes

    def merge_graph(self):
        for dir in self.args.input:
            try:
                file = open(dir+"/graph.json","r")
            except:
                print('Could not open '+dir+"/nodes.json")
                continue
            graph = json.load(file)
            if not graph:
                continue
            if self.graph:
                node_count = len(self.graph['batadv']['nodes'])
                for link in graph['batadv']['links']:
                    link['source'] += node_count
                    link['target'] += node_count
                    self.graph['batadv']['links'].append(link)
                self.graph['batadv']['nodes'].extend(graph['batadv']['nodes'])
            else:
                self.graph = graph

    def write_output(self):
        try:
            nodes = open(self.args.output+"/nodes.json","w")
        except:
            sys.exit('Could not write '+self.args.output+"/nodes.json")
        try:
            graph = open(self.args.output+"/graph.json","w")
        except:
            sys.exit('Could not write '+self.args.output+"/graph.json")
        json.dump(self.nodes, nodes)
        json.dump(self.graph, graph)

def main(argv):
    merger = Merger()
    merger.parse_args(argv)
    merger.merge_nodes()
    merger.merge_graph()
    merger.write_output()

if __name__ == "__main__":
    main(sys.argv)


