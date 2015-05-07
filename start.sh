#!/bin/bash
cd $(/bin/pwd -P)
python3 start.py $*
pkill python3
pkill Python