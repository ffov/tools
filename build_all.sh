#!/bin/bash

set -x 
#==========================================================
DEFAULT_GLUON_IMAGEDIR_PREFIX='/var/www/html/'
DEFAULT_GLUON_SITEDIR=`dirname \`pwd\``'/site/'
echo sitedir
echo $DEFAULT_GLUON_SITEDIR
DEFAULT_GLUON_DIR='../gluon'
GLUON_VERSION=""
VERSION=""
TARGETS=""
CORES=""
MAKE_OPTS=""

function set_not_passed_arguments () {
	if [[ $GLUON_DIR == "" ]]
	then
		GLUON_DIR=$DEFAULT_GLUON_DIR
	fi
	if [[ $GLUON_SITEDIR == "" ]]
	then
		GLUON_SITEDIR=$DEFAULT_GLUON_SITEDIR
	fi
	if [[ $GLUON_IMAGEDIR_PREFIX == "" ]]
	then
		GLUON_IMAGEDIR_PREFIX='/home/mpw/output'
	fi
	if [[ $CORES == "" ]]
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
			-j*|--cores*)
				if [[ $value =~ ^-?[0-9]+$ ]]
				then
					CORES=$value
				else
					display_usage
				fi
				;;
			-g*|--gluon-dir*)
				GLUON_DIR=$value
				;;
			-s*|--site-dir*)
				GLUON_SITEDIR=$value
				;;
			-o*|--output-prefix*)
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

function build_make_opts () {
	MAKE_OPTS="-C $GLUON_DIR GLUON_SITEDIR=$GLUON_SITEDIR -j$CORES V=s"
}

function update_site-ffms_repo () {
	git --git-dir=$GLUON_SITEDIR/.git --work-tree=$GLUON_SITEDIR fetch
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
	git --git-dir=$1/.git --work-tree=$1 fetch
	git --git-dir=$1/.git --work-tree=$1 checkout $2
}

function gluon_prepare_buildprocess () {
	make dirclean $MAKE_OPTS
	make update $MAKE_OPTS
	check_success
}

function set_targets () {
	TARGETS=`make $MAKE_OPTS GLUON_TARGET= 2> /dev/null |grep -v 'Please\|make'|sed -e 's/ \* //g'`
}

function check_success() {
	if [ $? != 0 ]
	then
		echo "Something went wrong, aborting."
		exit 1
	fi
}

function build_all_domains_and_all_targets () {
	for i in `git --git-dir=$GLUON_SITEDIR/.git --work-tree=$GLUON_SITEDIR branch -a|grep -v HEAD|grep origin/Domäne| sed -e 's/.*\/Domäne/Domäne/'`; do
		prefix=`echo $i|sed -e 's/Domäne-/domaene/'`
		imagedir=$GLUON_IMAGEDIR_PREFIX/$prefix/versions/v$VERSION
		mkdir -p $imagedir
		select_commit $GLUON_SITEDIR $i
		git --git-dir=$GLUON_SITEDIR/.git --work-tree=$GLUON_SITEDIR pull
		echo $TARGETS
		for j in $TARGETS
		do
			make clean $MAKE_OPTS GLUON_RELEASE=$GLUON_VERSION GLUON_TARGET=$j V=s -j$CORES GLUON_IMAGEDIR=$imagedir
			make $MAKE_OPTS GLUON_RELEASE=$GLUON_VERSION+$VERSION GLUON_BRANCH=stable GLUON_TARGET=$j GLUON_IMAGEDIR=$imagedir
			check_success
		done
		make manifest GLUON_RELEASE=$GLUON_VERSION+$VERSION GLUON_BRANCH=experimental GLUON_PRIORITY=0 $MAKE_OPTS GLUON_IMAGEDIR=$imagedir
		make manifest GLUON_RELEASE=$GLUON_VERSION+$VERSION GLUON_BRANCH=beta GLUON_PRIORITY=1 $MAKE_OPTS GLUON_IMAGEDIR=$imagedir
		make manifest GLUON_RELEASE=$GLUON_VERSION+$VERSION GLUON_BRANCH=stable GLUON_PRIORITY=3 $MAKE_OPTS GLUON_IMAGEDIR=$imagedir
	done
}

process_arguments "$@"
build_make_opts
update_site-ffms_repo
download_gluon_repo_if_nescessary
select_commit $GLUON_DIR $GLUON_VERSION
gluon_prepare_buildprocess
set_targets
build_all_domains_and_all_targets

