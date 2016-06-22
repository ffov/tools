#!/bin/bash
DEFAULT_WIFI_CHANNEL=1

authorized_keys="/etc/dropbear/authorized_keys"
user=root
sshOptionen="-q -oBatchMode=yes -oPasswordAuthentication=no -oConnectTimeout=10s -oStrictHostKeyChecking=no"

command_string=""
handle_wifi=0
handle_reboot=0
handle_networking=0

function throw_error () {
	echo ERROR: $1
	display_usage
	exit 1
}
function is_enabled () {
	if [[ "$1" =~ "enabled" ]]
	then
		return 0
	elif [[ "$1" =~ "disabled" ]]
	then
		return 1
	else
		throw_error "Invalid argument, must be ”enabled“ or ”disabled“."
	fi
}
function set_hostname () {
	if [[ ${#2} != "" ]]
	then
		command_string="$command_string uci set system.@system[0].hostname='$2';uci commit system;"
		handle_reboot=1
	else
		throw_error "Invalid hostname"
	fi
}
function set_channel () {
	if [[ $1 =~ [1]?[0-9] && $1 >0 && $1 < 14 ]]
	then
		command_string="$command_string uci set system.@system[0].hostname='$2';uci commit system;"
		if [[ $1 != $DEFAULT_WIFI_CHANNEL ]]
		then
			set_mesh_on_wifi "disabled"
		fi
		handle_wifi=1
	else
		throw_error "Invalid channel"
	fi
}
function set_mesh_on_wifi () {
	if is_enabled $1 
	then
		command_string="$command_string uci set wireless.client_radio0.disabled='0'; uci commit wireless;"
	else
		command_string="$command_string uci set wireless.client_radio0.disabled='1'; uci commit wireless;"
	fi
	handle_wifi=1
}
function set_mesh_on_wan () {
	if is_enabled $1 
	then
		command_string="$command_string uci set network.mesh_wan.auto='1'; uci commit network;"
	else
		command_string="$command_string uci set network.mesh_wan.auto='0'; uci commit network;"
	fi
	handle_networking=1
}
function set_mesh_on_lan () {
	if is_enabled $1 
	then
		command_string="$command_string for iface in $(cat /lib/gluon/core/sysconfig/lan_ifname); do uci del_list network.client.ifname=$iface; done; uci set network.mesh_lan.auto=1; uci commit network;"
	else
		command_string="$command_string for iface in $(cat /lib/gluon/core/sysconfig/lan_ifname); do uci add_list network.client.ifname=$iface; done; uci set network.mesh_lan.auto=0; uci commit network;"
	fi
	handle_networking=1
}
function set_location () {
	if [[ $co =~ [0-9]+\.[0-9]+,[\ ]?[0-9]+\.[0-9]+ ]]
	then
		lat=${1/,*}
		long=${1/*,}
		command_string="$command_string uci set gluon-node-info.@location[0].latitude=$lat;uci set gluon-node-info.@location[0].longitude=$long;uci set gluon-node-info.@location[0].share_location=1;uci commit gluon-node-info;"
	else
		throw_error "Ungültige Koordinaten"
	fi
}

function process_Arguments () {
	while [ ! -z "$1" ]
	do
		case "$1" in
			"-h|--hostname")
				set_hostname $2
				shift
				shift
				;;
			"-c|--set-channel")
				set_channel $2
				shift
				shift
				;;
			"-m|--set-mesh-on-wifi")
				set_mesh_on_wifi $2
				shift
				shift
				;;
			"-w|--set-mesh-on-wan")
				set_mesh_on_wan $2
				shift
				shift
				;;
			"-l|--set-mesh-on-lan")
				set_mesh_on_lan $2
				shift
				shift
				;;
			"-g|--set-location")
				set_location $2
				shift
				shift
				;;
		esac
		shift
	done
}

function areThereEnoughArgumentsGiven () {
	if [[ $# >= "3" ]]
	then
		return 0
	else
		return 1
	fi
}

function display_usage () {
	echo 'This tool can set certain options on a gluon node.'
	echo
	echo 'Usage: $0 [-h|--hostname <hostname>][-c|--set-channel <channel>][-m|--set-mesh-on-wifi <enabled|disabled>][-w|--set-mesh-on-wan <enabled|disabled>][-l|--set-mesh-on-lan <enabled|disabled>][-g|--set-location <"latitude,longitude">] host'
}

function ssh_on_node {
	ssh $sshOptionen $user@$1 $2
	return $?
}

if ! areThereEnoughArgumentsGiven
then
	display_usage
	exit 1
fi
process_Arguments "$@"
ssh_on_node $i "$command"
if [ ! $? == '0' ]
then
	echo "ERROR: $i fehlgeschlagen."
fi
