#!/bin/bash
cd ${0%/*}
python3 server.py &
python3 main.py 
echo "Press enter to continue..."
read
