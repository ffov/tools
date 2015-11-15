#!/bin/bash
for i in /proc/sys/net/ipv4/conf/bat*; do
    num=${i#*bat}
    mkdir -p /var/ffmap/data${num}
    /usr/src/ffmap-backend/backend.py -d /var/ffmap/data${num} -m bat${num}:/run/alfred${num}.sock 
done
mkdir -p /var/ffmap/legacy_data
wget https://freifunk-muensterland.de/map/data/nodes.json -O /var/ffmap/legacy_data/nodes.json
wget https://freifunk-muensterland.de/map/data/graph.json -O /var/ffmap/legacy_data/graph.json
mkdir -p /var/www/html/data
/usr/src/tools/merge_map_data.py -o /var/www/html/data /var/ffmap/legacy_data /var/ffmap/data*
