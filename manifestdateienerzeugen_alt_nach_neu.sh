#!/bin/bash

PRIORITY=0

cd $1
datum=`date -d @$(( $(date +"%s") - 604800)) +"%Y-%m-%d %H:%M:%S%:z"`
version=v2015.1.2+192
for i in stable beta experimental; do
	echo "BRANCH=$i" > $i.manifest
	echo "DATE=$datum" >> $i.manifest
	echo "PRIORITY=$PRIORITY" >> $i.manifest
	echo >> $i.manifest
	for j in *bin; do
		model=${j#*-*-*-*}
		model=${model%-sysupgrade.bin}
		pruefsumme=`sha512sum $j`
                pruef=${pruefsumme#*}
                pruef=${pruef%  $j}
		echo "$model $version $pruef $j" >> $i.manifest
	done
done

