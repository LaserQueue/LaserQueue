#!/bin/bash
cd $(/bin/pwd -P)
if [[ $EUID -ne 0 ]]; then
	echo 'attempting to elevate permissions'
	sudo -k ./start.sh $*
	exit 1
fi
python3 start.py $*
pkill python3
pkill Python