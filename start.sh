#!/bin/bash
if [[ $EUID -ne 0 ]]; then
	echo 'start.sh: Permission denied'
	exit 1
fi
cd $(/bin/pwd -P)
python3 start.py $*
pkill python3
pkill Python