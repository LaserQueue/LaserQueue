#!/bin/bash
cd ${0%/*}
cd ../www
sudo python3 -m http.server 80