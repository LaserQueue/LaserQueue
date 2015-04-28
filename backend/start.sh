#!/bin/bash
cd ${0%/*}
sleep 1
python3 server.py &
python3 main.py 
echo "Press enter to continue..."
read
pkill Python