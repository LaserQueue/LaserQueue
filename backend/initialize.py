import json
import os
import socket
import pip
import argparse

parser = argparse.ArgumentParser(prog='startbackend.sh')
parser.add_argument("-l", "--local", help="Run from localhost", dest="local",
	action="store_const",const=True,default=False)
parser.add_argument("-p", "--port", help="Port to host from", dest="port",
	default=80, type=int)
parser.add_argument("-b", "--queue-backup", help="Backup queue and load from backup on start", dest="backup",
	action="store_const",const=True,default=False)
parser.add_argument("-r", "--regen-config", help="Regenerate config.json", dest="regen",
	action="store_const",const=True,default=False)
parser.add_argument("-s", "--skip-install", help="Skip package installation", dest="skip",
	action="store_const",const=True,default=False)
parser.add_argument("--install-all", help="Don't ask for confirmation on install", dest="all",
	action="store_const",const=True,default=False)
args = parser.parse_args()

def qsort(l):
		if l == []: 
				return []
		else:
				pivot = l[0]
				lesser = qsort([x for x in l[1:] if x < pivot])
				greater = qsort([x for x in l[1:] if x >= pivot])
				return lesser + [pivot] + greater

def copyconf():
	data = json.load(open(os.path.join("..", "www", "defaultconf.json")))
	data["host"] = getIps()[0]
	json.dump(data, open(os.path.join("..", "www", "config.json"), "w"))

PACKAGES_UX = [
	"websockets",
	"netifaces"
]
PACKAGES_WIN = [
	"websockets",
	"netifaces",
	"pyserial",
	"pyautoit"
]
def getpacks():
	if args.skip: return
	pl = [str(i).split(" ")[0] for i in pip.get_installed_distributions()]
	packages = (PACKAGES_WIN if os.name == "nt" else PACKAGES_UX)
	installed = False
	for pack in packages:
		if pack in pl:
			continue
		installed = True
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
	if installed:
		for pack in packages:
			if pack not in pl:
				print("Failed to install all dependencies.")
	if installed:
		print("Sucessfully installed all dependencies!")

def _comparel(list1, list2):
	list1diff, list2diff = False, False
	for i in list1:
		if i not in list2:
			list1diff = True; break
	for i in list2:
		if i not in list1:
			list2diff = True; break
	if list1diff and list2diff: return "ne"
	elif list1diff:             return "l1"
	elif list2diff:             return "l2"
	else:                       return "eq"

def _fillblanks(odict, adict):
	keys = list(adict.keys())
	for i in keys:
		if i not in odict:
			odict[i] = adict[i]
	return odict

def main():
	getpacks()
	if args.regen or not os.path.exists(os.path.join("..", "www", "config.json")):
		copyconf()
	if args.local:
		data = json.load(open(os.path.join("..", "www", "config.json")))
		data["host"] = "localhost"
		json.dump(data, open(os.path.join("..", "www", "config.json"), "w"))
	else:
		data = json.load(open(os.path.join("..", "www", "config.json")))
		if data["host"] == "localhost":
			print("Last time you ran this program, it was in local mode.")
			confirm = ""
			while confirm not in ["y", "n"]:
				confirm = input("Do you want to regenerate the host? (y/n) ").lower().strip().rstrip()
			if confirm == "y":
				data["host"] = getIps()[0]
			json.dump(data, open(os.path.join("..", "www", "config.json"), "w"))
	data = json.load(open(os.path.join("..", "www", "config.json")))
	defaultdata = json.load(open(os.path.join("..", "www", "defaultconf.json")))
	keys = list(data.keys())
	dkeys = list(defaultdata.keys())
	equiv = _comparel(keys, dkeys)
	print(equiv) 
	if equiv == "ne" or equiv == "l2":
		print("Your config isn't storing the data expected.")
		print("Expected: "+", ".join(qsort(dkeys))+".")
		print("Found:    "+", ".join(qsort(keys))+".")
		confirm = ""
		while confirm not in ["y", "n"]:
			confirm = input("Do you want to regenerate the config? (y/n) ").lower().strip().rstrip()
		if confirm == "y":
			copyconf()
		else:
			print("Instead, you can add all missing tags to defaultconf.")
			confirm = ""
			while confirm not in ["y", "n"]:
				confirm = input("Do you want to add all missing tags? (y/n) ").lower().strip().rstrip()
			if confirm == "y":
				data = _fillblanks(data, defaultdata)
				json.dump(data, open(os.path.join("..", "www", "config.json"), "w"))
	print("Initialization complete.")

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