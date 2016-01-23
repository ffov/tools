#!/bin/bash
# Program name: pingall.sh
date
cat hostlist.txt |  while read output
do
    naddr=`echo $output | sed -e "s/:0:/:$2:/g"`
    ping6 -c 1 "$naddr" > /dev/null
    if [ $? -eq 0 ]; then
    sed -r -i.bak "/[ ]*$output(.*)/d" $1
    echo "node $naddr is up"
    else
    echo "node $naddr is down"
    ping6 -c 1 "$output" > /dev/null
    if [ $? -eq 0 ]; then
    echo "node $output is up" 
    else
    echo "node $output is down"
    sed -r -i.bak "/([ ]*$output[ ]+1;[ ]*)#(READY )*(.*)/ s//\1#READY \3/" $1
    fi
    fi
done

