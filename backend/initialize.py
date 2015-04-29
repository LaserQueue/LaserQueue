import json
import os.path
import socket

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--regen-config", help="Regenerate config.json", dest="regen")

def copyconf():
	data = json.load(open(os.path.join("..", "www", "defaultconf.json")))
	data["host"] = getIps()[0]
	json.dump(data, open(os.path.join("..", "www", "config.json"), "w"))

def main():
	args = parser.parse_args()
	if not os.path.exists(os.path.join("..", "www", "config.json")) or args.regen:
		copyconf()

def getIps():
	from netifaces import interfaces, ifaddresses, AF_INET
	ips = []
	for ifaceName in interfaces():
		addresses = [i['addr'] for i in ifaddresses(ifaceName).get(AF_INET, [{"addr":"not found"}])]
		if "not found" not in addresses and "127.0.0.1" not in addresses:
			ips += addresses
	return ips

if __name__ == "__main__":
	main()