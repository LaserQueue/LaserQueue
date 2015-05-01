import json
import os
import socket
import pip
import argparse

parser = argparse.ArgumentParser(prog='startbackend.sh')
parser.add_argument("-l", "--local", help="Run from localhost", dest="local",
	action="store_const",const=True,default=False)
parser.add_argument("-b", "--queue-backup", help="Backup queue and load from backup on start", dest="backup",
	action="store_const",const=True,default=False)
parser.add_argument("-r", "--regen-config", help="Regenerate config.json", dest="regen",
	action="store_const",const=True,default=False)
parser.add_argument("-s", "--skip-install", help="Skip package installation", dest="skip",
	action="store_const",const=True,default=False)
parser.add_argument("--install-all", help="Don't ask for confirmation on install", dest="all",
	action="store_const",const=True,default=False)
args = parser.parse_args()

def copyconf():
	data = json.load(open(os.path.join("..", "www", "defaultconf.json")))
	data["host"] = getIps()[0]
	json.dump(data, open(os.path.join("..", "www", "config.json"), "w"))

PACKAGES_UX = [
	"websockets",
	"Rocket",
	"netifaces"
]
PACKAGES_WIN = [
	"websockets",
	"Rocket",
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
			confirm = input("Install dependency "+pack+"? (y/n) ").lower().strip().rstrip()
		if confirm == "n": 
			print("WARNING: Program may not run without this library.")
			continue
		if pip.main(["install", pack]) and os.name != "nt":
			confirm = ("y" if args.all else "")
			while confirm not in ["y", "n"]:
				confirm = input("Install failed, try again with elevated permissions? (y/n) ").lower().strip().rstrip()
			if confirm == "n": 
				print("WARNING: Program may not run without this library.")
				continue
			os.system("sudo pip3 install "+pack)





def main():
	getpacks()
	if args.regen or not os.path.exists(os.path.join("..", "www", "config.json")):
		copyconf()
	print("initialization was successful")

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