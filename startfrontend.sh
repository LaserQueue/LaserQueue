#!/bin/bash
cd ${0%/*}
cd backend
python3 initialize.py $*
cd ../www
sudo python3 -m http.server 80