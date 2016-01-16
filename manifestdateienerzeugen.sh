#!/bin/bash

PRIORITY=0

cd $1
datum=`date +"%Y-%m-%d %H:%M:%S%:z"`

for i in stable beta experimental; do
	echo "BRANCH=$i" > $i.manifest
	echo "DATE=$datum" >> $i.manifest
	echo "PRIORITY=$PRIORITY" >> $i.manifest
	echo >> $i.manifest
	for j in *bin; do
		model=${j#*-*-*-*}
		model=${model%-sysupgrade.bin}
		version=${j#*-*-}
		version=${version%-$model-sysupgrade.bin}
		pruefsumme=`sha512sum $j`
		echo "$model $version $pruefsumme" >> $i.manifest
	done
done

