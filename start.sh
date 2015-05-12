#!/bin/bash
cd $(/bin/pwd -P)
python3 start.py $* && echo "import os;os.remove(\"/tmp/toscript.json\");os.remove(\"/tmp/topage.json\")" | python3 >/dev/null
pkill python3
pkill Python