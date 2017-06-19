#!/bin/bash

REFERENCE="domaenenliste:"

HOSTS_FILE=""
CONFIG_TABLE_FILE=""

GATEWAY_DOMAIN_LIST=""
GATEWAY_DOMAIN_ID=""

OUTPUT_FILE=""

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
			return 0
		elif [[ $preGatewaysLine -gt 0 ]]
		then
			echo $(echo $line|cut -f1 -d' ')
		fi
	done < $HOSTS_FILE
	return 0
}

function file_exists_and_has_size_greater_zero () {
	[[ -s "$1" ]] && return 0 || return 1
}

function set_hosts_file () {
	if file_exists_and_has_size_greater_zero "$1"
	then
		HOSTS_FILE="$1"
		return 0
	else
		echo "The given hosts file could not be found or is empty. Please give the hosts file of the ansible repository as first argument."
		exit 1
	fi
}

function set_config_table_file {
	if file_exists_and_has_size_greater_zero "$1"
	then
		CONFIG_TABLE_FILE="$1"
		return 0
	else
		echo "The given config table file could not be found or is empty. Please give the file as second argument."
		exit 1
	fi
}

function read_config_table_file_and_set_gateway_domain_array () {
	count=0
	while IFS='' read -r line || [[ -n "$line" ]]; 
	do 
		if [[ $line =~ "$1" ]]
		then
			dom=$(echo $line |cut -d" " -f1)
			GATEWAY_DOMAIN_LIST[$count]=${dom:(-2)}
			if [[ $(echo $line |cut -d" " -f2) == "$1" ]]
			then
				GATEWAY_DOMAIN_ID[$count]=2
			else
				GATEWAY_DOMAIN_ID[$count]=3
			fi
		fi
		count=$((count + 1))

	done < "$CONFIG_TABLE_FILE"
}

function set_out_file () {
	OUTPUT_FILE="${HOSTS_FILE:0:(-1)}_vars/$1_neu"
	if [[ -e $OUTPUT_FILE ]]
	then
		echo "There is already a file at the specified output path $OUTPUT_FILE for the new configuration file. Do you want to delete it?"
		rm -i $OUTPUT_FILE
	fi
}

function copy_old_config_till_reference () {
	while IFS='' read -r line
	do
		echo $line >> "$OUTPUT_FILE"
		if [[ $line =~ "$REFERENCE" ]]
		then
			return 0
		fi
	done < ${HOSTS_FILE:0:(-1)}_vars/$1

}

function copy_rest_of_old_config_file () {
	section=0
	while IFS='' read -r line
	do
		if [[ $section == "0" ]]
		then
			if [[ $line =~ "$REFERENCE" ]]
			then 
				section=1
			fi
		elif [[ $section == "1" ]]
		then
			if [[ -z $line || ${line:0:1} != " " ]]
			then
				section=2
				echo $line >> $OUTPUT_FILE
			fi
		else
			echo $line >> $OUTPUT_FILE
		fi
	done < ${HOSTS_FILE:0:(-1)}_vars/$1
}

function generate_config_for_gateway () {
	echo ">>> HIER KOMMT DER NEUE BLOCK REIN <<< " >> $OUTPUT_FILE
}

function write_config_in_gateway_hosts_file () {
	set_out_file $1
	copy_old_config_till_reference $1
	generate_config_for_gateway $1
	copy_rest_of_old_config_file $1
}



set_hosts_file "$1"
set_config_table_file "$2"

gateways=$(read_gateways_from_hosts_file)

for gateway in $gateways
do
	read_config_table_file_and_set_gateway_domain_array $gateway
	write_config_in_gateway_hosts_file $gateway

done
	





