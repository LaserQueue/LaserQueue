#!/bin/bash
cd $(/bin/pwd -P)
python3 start.py $*
rm /tmp/toscript.json >/dev/null
rm /tmp/topage.json >/dev/null
pkill python3
pkill Python