#!/bin/bash

authorized_keys="/etc/dropbear/authorized_keys"
user=root
sshOptionen="-q -oBatchMode=yes -oPasswordAuthentication=no -oConnectTimeout=10s -oStrictHostKeyChecking=no"

counter_keys_to_add=0
counter_keys_to_delete=0
counter_hosts=0

keys_to_add=()
keys_to_delete=()
hosts=()

function add_key () {
	if [ ! -s "$1" ]
	then
		echo "WARNING: $i does not exist, skipping."
	else 
		counter_keys_to_add=$(( $counter_keys_to_add + 1 ))
		keys_to_add[$counter_keys_to_add]=$1
	fi
}

function delete_key () {
	if [ ! -s "$1" ]
	then
		echo "WARNING: $i does not exist, skipping."
	else 
		counter_keys_to_delete=$(( $counter_keys_to_delete + 1 ))
		keys_to_delete[$counter_keys_to_delete]=$1
	fi
}

function add_host () {
	counter_hosts=$(( $counter_hosts + 1 ))
	hosts[$counter_hosts]=$1
}

function process_Arguments () {
	while [ ! -z "$1" ]
	do
		case "$1" in
			"-a")
				add_key $2
				shift
				;;
			"-d")
				delete_key $2
				shift
				;;
			*)
				add_host $1
				;;
		esac
		shift
	done
}

function areThereEnoughArgumentsGiven () {
	if [[ ( $counter_keys_to_add -gt 0 || $counter_keys_to_delete -gt 0 ) && $counter_hosts -gt 0 ]]
	then
		return 0
	else
		return 1
	fi
}

function display_usage () {
	echo 'This tool adds or removes public ssh keys from multiple hosts.'
	echo
	echo 'Usage: $0 [-a public_keyfile|-d public_keyfile]... host [host]...'
}

function compose_command_string () {
	command='if [[ ! `tail -c 1 '$authorized_keys'` == "" ]];then echo >> '$authorized_keys';fi;'
	for i in "${keys_to_add[@]}"
	do
		key=`cat $i`
		command="$command""echo $key >> $authorized_keys;"
	done
	if [[ $counter_keys_to_delete -gt 0 ]]; then
		command="$command"" sed "
		for i in "${keys_to_delete[@]}"
		do
			key=`cat $i |cut -f2 -d" "`
			command="$command"" -i '\#$key#d'"
		done
		command="$command"" $authorized_keys;"
	fi
	echo $command
}

function ssh_on_node {
	ssh $sshOptionen $user@$1 $2
	return $?
}

process_Arguments "$@"

if ! areThereEnoughArgumentsGiven
then
	display_usage
	exit 1
fi

command=$(compose_command_string)


for i in "${hosts[@]}"
do
	ssh_on_node $i "$command"
	if [ ! $? == '0' ]
	then
		echo "ERROR: $i fehlgeschlagen."
	fi
done


