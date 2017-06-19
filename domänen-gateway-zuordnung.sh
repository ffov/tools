#!/bin/bash

function read_gateways_from_hosts_file () {
	preGatewaysLine=0

	while IFS='' read -r line || [[ -n "$line" ]]; do
		if [[ $preGatewaysLine == 0 ]]
		then
			if [[ "$line" =~ "[gateways]" ]]
			then
				preGatewaysLine=1
			fi
		elif [[ -z "$line" || ${line:0:1} == '[' ]]
		then
			echo "Ende gefunden"
			return 0
		elif [[ $preGatewaysLine -gt 0 ]]
		then
			echo $(echo $line|cut -f1 -d' ')
		fi
	done < "$1"
	return 0
}

read_gateways_from_hosts_file "$1"



