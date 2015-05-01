#!/bin/bash
cd ${0%/*}
sleep 1
python3 server.py $* &
python3 main.py $*
pkill Python
pkill python3