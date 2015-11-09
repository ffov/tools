#!/bin/bash

cd /root/Downloads/ffmap-backend
for i in /proc/sys/net/ipv4/conf/bat*; do
    num=${i#*bat}
    mkdir -p data${num}
    ./backend.py -d data${num} -m bat${num}:/run/alfred${num}.sock 
done
mkdir -p legacy_data
wget https://freifunk-muensterland.de/map/data/nodes.json -O legacy_data/nodes.json
wget https://freifunk-muensterland.de/map/data/graph.json -O legacy_data/graph.json
./merge_map_data.py -o /var/www/html/data legacy_data data*
