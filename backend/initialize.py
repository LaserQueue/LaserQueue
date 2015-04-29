import json
import os
import socket
import pip
import argparse

parser = argparse.ArgumentParser(description='A foo that bars',
                                 prog='startbackend.sh')
parser.add_argument("-r", "--regen-config", help="Regenerate config.json", dest="regen")
parser.add_argument("-s", "--skip-install", help="Skip package installation", dest="skip")
parser.add_argument("--install-all", help="Don't ask for confirmation on install", dest="all")
args = parser.parse_args()

def copyconf():
	data = json.load(open(os.path.join("..", "www", "defaultconf.json")))
	data["host"] = getIps()[0]
	json.dump(data, open(os.path.join("..", "www", "config.json"), "w"))

PACKAGES_UX = [
	"netifaces"
]
PACKAGES_WIN = [
	"netifaces",
	"pyserial",
	"pyautoit"
]
def getpacks():
	if args.skip: return
	pl = [str(i).split(" ")[0] for i in pip.get_installed_distributions()]
	packages = (PACKAGES_WIN if os.name == "nt" else PACKAGES_UX)
	for pack in packages:
		if pack in pl:
			continue
		confirm = ("y" if args.all else "")
		while confirm not in ["y", "n"]:
			confirm = input("Continue with installation of "+pack+"? (y/n) ").lower().strip().rstrip()
		if confirm == "n": 
			print("WARNING: Program may not run without this library.")
			continue
		pip.main(["install", pack])




def main():
	if not os.path.exists(os.path.join("..", "www", "config.json")) or args.regen:
		copyconf()
	getpacks()

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