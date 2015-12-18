#!/bin/bash
for i in /proc/sys/net/ipv4/conf/bat*; do
    num=${i#*bat}
    mkdir -p /var/www/html/data${num}
    /usr/src/ffmap-backend/backend.py -d /var/www/html/data${num} -m bat${num}:/run/alfred.$(printf %02d ${num}).sock 
done
mkdir -p /var/www/html/data_waf
wget http://ffwaf-srv2.freifunk-muensterland.net/o/nodes.json -O /var/www/html/data_waf/nodes.json
wget http://ffwaf-srv2.freifunk-muensterland.net/o/graph.json -O /var/www/html/data_waf/graph.json
mkdir -p /var/www/html/legacy_data
wget https://freifunk-muensterland.de/map/data_alt/nodes.json -O /var/www/html/legacy_data/nodes.json
wget https://freifunk-muensterland.de/map/data_alt/graph.json -O /var/www/html/legacy_data/graph.json
mkdir -p /var/www/html/data
/usr/src/tools/merge_map_data.py -o /var/www/html/data /var/www/html/legacy_data /var/www/html/data?*

for i in /var/www/html/data?*; do
    suf=${i#*data}
    if [ ! -e /var/www/html/map${suf} ]; then
        mkdir /var/www/html/map${suf} && cd /var/www/html/map${suf} && ln -s ../map/* . && rm config.json && sed -e "s#/data/#/data$suf/#" -e "s#Münsterland#Münsterland - Domäne ${suf}#" <../map/config.json >config.json
        cat <<EOF > /var/www/html/index.html
<html>
<head>
<meta charset="UTF-8">
<title>Freifunk Münsterland</title>
</head>
<body>
<h1>Freifunk Münsterland - Karten</h1>
<p><a href="map/">Gesamtkarte</a></p>
EOF
	for j in /var/www/html/data?*; do
	    suf2=${j#*data}
	    name=$(echo $suf2 | sed -e s/_waf/Warendorf/)
	    echo "<p><a href=\"map$suf2/\">Domäne $name</a></p>" >> /var/www/html/index.html
        done
        cat <<EOF >> /var/www/html/index.html
</body>
</html>
EOF
    fi
done
