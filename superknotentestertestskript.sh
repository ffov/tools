#!/bin/bash

privaterSchluessel="" # << Hier den Pfad zum privaten Schlüssel eintragen, dürfte /home/$USER/.ssh/id_rsa sein
speedtest="" # << Hier den Pfad zur speedtest_cli.py eintragen

testrouter=10.43.0.1
ausweichip=10.43.99.99
netz="10.43.0.0/16"
lan=eth0
testbefehle="ip route show default;ip -6 route show default;ping6 -n -c2 google.de;batctl gwl"
ausgabedatei=superknotentester.log


################################################
sshOptionen="-q -i $privaterSchluessel -oBatchMode=yes -oPasswordAuthentication=no -oConnectTimeout=10s -oStrictHostKeyChecking=no"
superknoten=()
function testdurchlauf () {
	echo
	echo 'Tests auf dem Router:'
	echo
	ssh $sshOptionen root@$testrouter "wget -qO - localhost/cgi-bin/status|grep -i 'connected\|vpn\|fastd'" 
	ssh $sshOptionen root@$testrouter "$testbefehle"
	echo
	echo 'Tests auf diesem Rechner:'
	echo
	ip address show $lan
	ip route show default
	ip -6 route show default
	ping -n -c2 google.de
	ping6 -n -c2 google.de
	traceroute google.de
	traceroute6 google.de
	$speedtest
}
function routerPraeparieren () {
	ssh $sshOptionen root@$testrouter "uci set autoupdater.settings.branch=experimental;uci commit; autoupdater -f"
	echo 'Warten bis Router wieder erreichbar ist, falls ein Update durchgeführt wurde...'
	false
	while [ $? != 0 ]; do
		ssh $sshOptionen root@$testrouter "ls /tmp &> /dev/null"
	done
	echo 'Router ist bereit. Konfiguriere nun den Router.'
	ssh $sshOptionen root@$testrouter "uci set wireless.client_radio0.disabled=1;uci set wireless.mesh_radio0.disabled=1;uci set wireless.mesh_radio1.disabled=1;uci set wireless.client_radio1.disabled=1;wifi"
}
function welcheSuperknotenGibtEs () {
	ausgabe=`ssh $sshOptionen root@$testrouter "uci show fastd|grep -i mesh_vpn_backbone_peer|grep -i enabled"`
	counter=0
	for i in $ausgabe; do
		i=${i##fastd.mesh_vpn_backbone_peer_}
		superknoten[$counter]=${i%%.enabled=*}
		counter=$((counter+1))
	done
}
function binIchRoot () {
	if [ "$(id -u)" != "0" ]; then
		echo "Dieses Skript benötigt Root-Rechte!" 1>&2
		exit 1
	fi
}
function routerErreichbar () {
	ping -c2 $testrouter &> /dev/null
	if [ "$?" != "0" ]; then
		return 1
	else 
		return 0
	fi
}
function ausweichIpVerwenden () {
	sudo ip addr flush dev $lan
	sudo ip route flush dev $lan
	sudo ip addr add $ausweichip/16 dev $lan
	sudo ip route add $netz	dev $lan
}
function verbindungSonstEnde() {
	sudo dhclient -nw $lan
	if ! routerErreichbar; then
		echo 'Router nicht erreichbar, noch 20 Sekunden warten.'
		sleep 20s
	fi
	if routerErreichbar; then
		return 0	
	else 
		echo 'Kein DHCP, verwende Ersatzip.'
		killall -9 dhclient
		ausweichIpVerwenden 
		if routerErreichbar; then
			return 0
		else 
			echo "Der Testrouter ist nicht erreichbar, bitte stelle sicher, dass LAN-Mesh deaktiviert ist und dieser Computer über $lan mit einem LAN-Port am Router verbunden ist. Dieses Skript funktioniert nicht mit Routern, die nur eine LAN-Schnittstelle haben, wie z.B. die Picostation oder die Bullet."
			exit 1
		fi
	fi
}
function fastdAufZuTestendenSuperknotenEinstellen {
	befehl=""
	for i in "${superknoten[@]}"; do 
		if [ "$i" == "$1" ]; then
			befehl="$befehl uci set fastd.mesh_vpn_backbone_peer_$i.enabled=1;"
		else 
			befehl="$befehl uci set fastd.mesh_vpn_backbone_peer_$i.enabled=0;"
		fi
	done
	befehl="$befehl /etc/init.d/fastd restart;"
	ssh $sshOptionen root@$testrouter "$befehl"
}
function speedtestMoeglich {
	if which python; then
		if [ -n "$speedtest" && -s "$speedtest" ]; then
			return 0
		else 
			wget https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest_cli.py
			chmod +x speedtest_cli.py
			speedtest="./speedtest_cli.py"
		fi
	else
		echo 'Kein Python verfügbar, deaktiviere Speedtest'
		speedtest="echo 'Speedtest nicht verfügbar'"
	fi
}
function aufraeumen {
	ssh $sshOptionen root@$testrouter "reboot;exit"
	sudo service network-manager start
}

binIchRoot &>> $ausgabedatei
sudo service network-manager stop &>> $ausgabedatei
date &>> $ausgabedatei
verbindungSonstEnde &>> $ausgabedatei
routerPraeparieren &>> $ausgabedatei
welcheSuperknotenGibtEs &>> $ausgabedatei
speedtestMoeglich &>> $ausgabedatei

for i in "${superknoten[@]}"; do
	echo &>> $ausgabedatei
	echo &>> $ausgabedatei
	echo '=======================' &>> $ausgabedatei
	echo "Nun wird $i getestet." &>> $ausgabedatei
	date &>> $ausgabedatei
	echo &>> $ausgabedatei
	fastdAufZuTestendenSuperknotenEinstellen "$i" &>> $ausgabedatei
	verbindungSonstEnde &>> $ausgabedatei
	testdurchlauf &>> $ausgabedatei
done
aufraeumen &>> $ausgabedatei
date &>> $ausgabedatei
echo "ENDE" &>> $ausgabedatei
echo &>> $ausgabedatei
