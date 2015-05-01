#!/bin/bash
cd ${0%/*}

cd backend
python3 initialize.py $*
cd ..
./startfrontend.sh $* &
./startbackend.sh $* 