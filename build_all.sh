#!/bin/bash

set -x 
#==========================================================
DEFAULT_GLUON_IMAGEDIR_PREFIX='/var/www/html/'
DEFAULT_GLUON_SITEDIR='/home/mpw/gits/site-ffms/'
DEFAULT_GLUON_DIR='gluon'
GLUON_VERSION=""
VERSION=""
TARGETS=""
CORES=""
WORKINGDIR=""

function set_not_passed_arguments () {
	if [[ $GLUON_DIR == "" ]]
	then
		GLUON_DIR=$DEFAULT_GLUON_DIR
	fi
	if [[ $GLUON_SITEDIR == "" ]]
	then
		GLUON_SITEDIR=$DEFAULT_GLUON_SITEDIR
	fi
	if [[ $GLUON_IMAGEDIR_PREFIX = "" ]]
	then
		GLUON_IMAGEDIR_PREFIX='/home/mpw/output'
	fi
	if [[ $CORES="" ]]
	then
		CORES=`cat /proc/cpuinfo |grep -i 'model name'|wc -l`
	fi
}

function split_value_from_argument () {
	if [[ "${1:1:1}" == '-' ]]
	then
	       	if [[ "$1" =~ '=' ]]
		then
			echo ${1##*=}
		else
			echo $2
			return 1
		fi
	else
		if [[ "${#1}" == 2 ]]
		then
			echo $2
			return 1
		else
			echo ${1:2}
		fi
	fi
	return 0
}

function process_arguments () {
	while [[ "${1:0:1}" == "-" ]]
	do
		arg=$1
		value=`split_value_from_argument $1 $2`
		if [[ $? == 1 ]] 
		then
			shift
		fi
		case "$arg" in
			"-j*|--cores*")
				if [[ $value =~ ^-?[0-9]+$ ]]
				then
					CORES=$value
				else
					display_usage
				fi
				;;
			"-g*|--gluon-dir*")
				GLUON_DIR=$value
				;;
			"-s*|--site-dir*")
				GLUON_SITEDIR=$value
				;;
			"-o*|--output-prefix*")
				GLUON_IMAGEDIR_PREFIX=$value
				;;
		esac
		shift
	done
	if [[ $1 == "" || $2 == "" ]]
	then
		display_usage
	else	
		GLUON_VERSION=$1
		VERSION=$2
	fi
	set_not_passed_arguments
}

function update_site-ffms_repo () {
	git fetch
}

function display_usage () {
echo 'Usage: $0 [(-j|--cores <Number of cores to use>)|(-g|--gluon-dir) <Path to Gluon-Git>|(-s|--site-dir) <Path to site.conf folder>|(-o|--output-prefix) <output path prefix>] Gluon_release_tag Gluon_version'
	exit 1
}

function download_gluon_repo_if_nescessary () {
	if [ ! -d $GLUON_DIR ]; then
		git clone https://github.com/freifunk-gluon/gluon.git $GLUON_DIR
	fi
}	

function select_commit () {
	cd $GLUON_DIR
	git fetch
	git checkout $1
	cd $WORKINGDIR
}

function gluon_prepare_buildprocess () {
	cd $GLUON_DIR
	make dirclean GLUON_SITEDIR=$GLUON_SITEDIR V=s -j$CORES
	make update GLUON_SITEDIR=$GLUON_SITEDIR V=s -j$CORES
	check_success
	cd $WORKINGDIR
}

function set_targets () {
	TARGETS=`ls $GLUON_DIR/targets | grep -v targets.mk`
}

function check_success() {
	if [ $? != 0 ]
	then
		echo "Something went wrong, aborting."
		exit 1
	fi
}

function build_all_domains_and_all_targets () {
	for i in `git branch -a|grep -v HEAD|grep origin/Domäne| sed -e 's/.*\/Domäne/Domäne/'`; do
		prefix=`echo $i|sed -e 's/Domäne-/domaene/'`
		imagedir=$GLUON_IMAGEDIR_PREFIX/$prefix/versions/v$VERSION
		mkdir -p $imagedir
		git checkout $i
		git pull
		cd $GLUON_DIR
		for j in $TARGETS
		do
			make clean GLUON_SITEDIR=$GLUON_SITEDIR GLUON_RELEASE=$GLUON_VERSION GLUON_TARGET=$j V=s -j$CORES
			make GLUON_RELEASE=$GLUON_VERSION+$VERSION GLUON_BRANCH=stable GLUON_TARGET=$j GLUON_IMAGEDIR=$imagedir GLUON_SITEDIR=$GLUON_SITEDIR V=s -j$CORES
			check_success
			make manifest GLUON_RELEASE=$GLUON_VERSION+$VERSION GLUON_BRANCH=experimental GLUON_PRIORITY=0 GLUON_SITEDIR=$GLUON_SITEDIR
			make manifest GLUON_RELEASE=$GLUON_VERSION+$VERSION GLUON_BRANCH=beta GLUON_PRIORITY=1 GLUON_SITEDIR=$GLUON_SITEDIR
			make manifest GLUON_RELEASE=$GLUON_VERSION+$VERSION GLUON_BRANCH=stable GLUON_PRIORITY=3 GLUON_SITEDIR=$GLUON_SITEDIR
		done
	done
}

function get_path () {
	WORKINGDIR=`pwd`
}

get_path
process_arguments "$@"
update_site-ffms_repo
download_gluon_repo_if_nescessary
select_commit $GLUON_VERSION
gluon_prepare_buildprocess
set_targets
build_all_domains_and_all_targets

