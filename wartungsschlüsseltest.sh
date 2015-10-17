	#!/bin/bash

# Dieses Werkzeug probiert sich mit dem privaten Schlüssel auf allen Knoten aus der
# nodes.json einzuloggen, um zu testen, ob der Schlüssel installiert ist. Somit
# kann getestet werden, auf welche Knoten man von außen Zugriff hat.

# Konfiguration:

AUSGABEDATEI="ipv6s-mit-Fernwartungskey.txt"
PFAD_ZUR_PRIVATEN_SCHLUESSELDATEI_OHNE_PASSWORT="/home/mpw/freifunk-muenster-fernwartung"

anzahlParalleleAbfragen="30"
ipv6Praefix="2a03:2260:115"
linkZurNodesJson="https://freifunk-muensterland.de/map/data/nodes.json"


# ===========================================

ipv6s=""

function testeAbhaengigkeiten() {
	which parallel &> /dev/null
	if [[ $? != 0 ]]; then
		echo 'Das Programm „parallel” wird benötigt, ist aber nicht installiert. Bitte installiere es mit dem Paketmanager deiner Distribution, z.B. mit „sudo apt-get install parallel“.'
		exit 1
	fi
}
function perSchluesselAnmeldenMoeglichTestUndLoggen() {
	timeout 30s ssh -x -q -i $PFAD_ZUR_PRIVATEN_SCHLUESSELDATEI_OHNE_PASSWORT -oIdentityFile=/dev/null -oBatchMode=yes -oPasswordAuthentication=no -oConnectTimeout=10s -oConnectionAttempts=2 -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null root@$1 true
	if [[ $? == 0 ]]; then
		echo "Erfolgreich auf $1 eingeloggt, speichere IPv6-Adresse."
		echo $1 erfolgreich >> $AUSGABEDATEI
	else	
		echo "Fehlgeschlagen auf $1."
	fi
	return $?
}
function ipv6AusNodesJsonParsen() {
	ipv6s=`wget -qO - $linkZurNodesJson|grep -i "$ipv6Praefix"|sed -e "s/.*\($ipv6Praefix.*\)\".*/\1/g"|uniq`
}

rm $AUSGABEDATEI &> /dev/null
testeAbhaengigkeiten
ipv6AusNodesJsonParsen
export AUSGABEDATEI=$AUSGABEDATEI
export PFAD_ZUR_PRIVATEN_SCHLUESSELDATEI_OHNE_PASSWORT=$PFAD_ZUR_PRIVATEN_SCHLUESSELDATEI_OHNE_PASSWORT
export -f perSchluesselAnmeldenMoeglichTestUndLoggen
echo $ipv6s|sed -e 's/ /\n/g' | parallel -P $anzahlParalleleAbfragen perSchluesselAnmeldenMoeglichTestUndLoggen {}
