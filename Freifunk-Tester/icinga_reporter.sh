#!/bin/bash

MAX_AGE=10800
DATA_PATH='.'

tail -n-1 $1_$2_$3
time=$(date -r $1_$2_$3 +%s)
now=$(date +%s)
diff=$(( $time - $now ))
if [[ $diff -gt $MAX_AGE ]]
then
	exit 3
else
	exit $(head -n1 $1_$2_$3)
fi

