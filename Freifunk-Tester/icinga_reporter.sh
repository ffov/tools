#!/bin/bash

MAX_AGE=10800
DATA_PATH='/root/testresults'
FILENAME="$DATA_PATH/$1_$2_$3"

tail -n +2 $FILENAME
time=$(date -r $FILENAME +%s)
now=$(date +%s)
diff=$(( $now - $time ))
if [[ $diff -gt $MAX_AGE ]]
then
	exit 3
else
	exit $(head -n1 $FILENAME)
fi

