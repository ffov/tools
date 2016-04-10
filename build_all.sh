#!/bin/bash

DEFAULT_GLUON_IMAGEDIR_PREFIX='/var/www/html/'
DEFAULT_GLUON_SITEDIR=`dirname \`pwd\``'/site/'
DEFAULT_SITE_URL="https://github.com/FreiFunkMuenster/site-ffms.git"
DEFAULT_GLUON_URL="https://github.com/freifunk-gluon/gluon.git"
DEFAULT_GLUON_DIR='../gluon'
GLUON_VERSION=""
VERSION=""
TARGETS=""
CORES=""
MAKE_OPTS=""
DOMAINS_TO_BUILD=""
TARGETS_TO_BUILD=""
SITE_URL=""
GLUON_URL=""
imagedir=""

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
	if [[ $SITE_URL == "" ]]
	then
		SITE_URL=$DEFAULT_SITE_URL
	fi
	if [[ $GLUON_URL == "" ]]
	then
		GLUON_URL=$DEFAULT_GLUON_URL
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
function enable_debugging () {
	set -x
}
function add_domain_to_buildprocess () {
	DOMAINS_TO_BUILD="$DOMAINS_TO_BUILD $1"
}

function add_target_to_buildprocess () {
	DOMAINS_TO_BUILD="$DOMAINS_TO_BUILD $1"
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
				shift
				;;
			-g*|--gluon-dir*)
				GLUON_DIR=$value
				shift
				;;
			-s*|--site-dir*)
				GLUON_SITEDIR=$value
				shift
				;;
			-o*|--output-prefix*)
				GLUON_IMAGEDIR_PREFIX=$value
				shift
				;;
			--gluon-url*)
				GLUON_URL=$value
				shift
				;;
			--site-url*)
				SITE_URL=$value
				shift
				;;
			-D|--enable-debugging)
				enable_debugging
				;;
			-d*|--domain*)
				add_domain_to_buildprocess $value
				shift
				;;
			-t*|--target*)
				add_target_to_buildprocess $value
				shift
				;;
		esac
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

function is_folder_a_git_repo () {
	git status --git-dir=$1/.git --work-tree=$1
	if [ $? != 0 ]
	then
		echo "The folder \"$1\" is not a valid git repository, delete it or select another destination and restart the script."
		exit 1
	fi
	return 0
}

function display_usage () {
echo 'Usage: $0 [(-j|--cores <Number of cores to use>)|(-g|--gluon-dir) <Path to Gluon-Git>|(-s|--site-dir) <Path to site.conf folder>|(-o|--output-prefix) <output path prefix>] Gluon_release_tag Gluon_version'
	exit 1
}

function is_folder () {
	[[ -d $1 ]] && return 0 || return 1
}

function git_fetch () {
	git --git-dir=$1/.git --work-tree=$1 fetch
}

function git_checkout () {
	git --git-dir=$1/.git --work-tree=$1 checkout $2
}

function git_pull () {
	git --git-dir=$1/.git --work-tree=$1 pull
}

function prepare_repo () {
	if [[ `is_folder $1` && `is_folder_a_git_repo $1` ]]
	then
		git_fetch $1
	else
		git clone $2 $1
	fi
}

function gluon_prepare_buildprocess () {
	make dirclean $MAKE_OPTS
	make update $MAKE_OPTS
	check_success
}

function get_all_targets_from_gluon_repo () {
	echo `make $MAKE_OPTS GLUON_TARGET= 2> /dev/null |grep -v 'Please\|make'|sed -e 's/ \* //g'`
}

function check_targets () {
	if [[ $TARGETS == "" ]]
	then
		TARGETS=${get_all_domains_from_site_repo}
	fi
}

function get_all_domains_from_site_repo () {
	echo `git --git-dir=$GLUON_SITEDIR/.git --work-tree=$GLUON_SITEDIR branch -a|grep -v HEAD|grep origin/Domäne| sed -e 's/.*\/Domäne/Domäne/'`
}

function check_domains () {
	if [[ $DOMAINS_TO_BUILD == "" ]]
	then
		DOMAINS_TO_BUILD=${get_all_domains_from_site_repo}
	fi
}

function check_success() {
	if [ $? != 0 ]
	then
		echo "Something went wrong, aborting."
		exit 1
	fi
}

function build_target_for_domaene () {
	make clean $MAKE_OPTS GLUON_RELEASE=$GLUON_VERSION GLUON_TARGET=$1 V=s -j$CORES GLUON_IMAGEDIR=$imagedir
	make $MAKE_OPTS GLUON_RELEASE=$GLUON_VERSION+$VERSION GLUON_BRANCH=stable GLUON_TARGET=$1 GLUON_IMAGEDIR=$imagedir
	check_success
}

function make_manifests () {
	make manifest GLUON_RELEASE=$GLUON_VERSION+$VERSION GLUON_BRANCH=experimental GLUON_PRIORITY=0 $MAKE_OPTS GLUON_IMAGEDIR=$imagedir
	make manifest GLUON_RELEASE=$GLUON_VERSION+$VERSION GLUON_BRANCH=beta GLUON_PRIORITY=1 $MAKE_OPTS GLUON_IMAGEDIR=$imagedir
	make manifest GLUON_RELEASE=$GLUON_VERSION+$VERSION GLUON_BRANCH=stable GLUON_PRIORITY=3 $MAKE_OPTS GLUON_IMAGEDIR=$imagedir
}


function build_selected_targets_for_domaene () {
	prefix=`echo $1|sed -e 's/Domäne-/domaene/'`
	imagedir=$GLUON_IMAGEDIR_PREFIX/$prefix/versions/v$VERSION
	mkdir -p $imagedir
	git_checkout $GLUON_SITEDIR $1
	git_pull $GLUON_SITEDIR
	for j in $TARGETS
	do
		build_target_for_domaene $j
	done
	make_manifests
}

function build_selected_domains_and_selected_targets () {
	for i in $DOMAINS_TO_BUILD
	do
		build_selected_targets_for_domaene $i
	done
}

process_arguments "$@"
build_make_opts
prepare_repo $GLUON_SITEDIR $SITE_URL
prepare_repo $GLUON_DIR $GLUON_URL
git_checkout $GLUON_DIR $GLUON_VERSION
gluon_prepare_buildprocess
check_targets
check_domains
build_selected_domains_and_selected_targets
