import json
import os
import socket
import pip
import argparse
import urllib.request
from math import ceil

parser = argparse.ArgumentParser(prog='startbackend.sh')
parser.add_argument("-l", "--local", help="Run from localhost", dest="local",
	action="store_const",const=True,default=False)
parser.add_argument("-p", "--port", help="Port to host from", dest="port",
	default=80, type=int)
parser.add_argument("-n", "--regen-host", help="Regenerate host in config", dest="host",
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
	if os.path.exists(os.path.join("..", "www", "userconf.json")):
		userdata = json.load(open(os.path.join("..", "www", "userconf.json")))
	else:
		userdata = {}
	data = _fillblanks(userdata, data)
	data["host"] = getIps()[0]
	json.dump(data, open(os.path.join("..", "www", "config.json"), "w"), indent=2)

PACKAGES_UX = [
	"websockets",
	"netifaces",
	"GitPython"
]
PACKAGES_WIN = [
	"websockets",
	"netifaces",
	"pyserial",
	"pyautoit",
	"GitPython"
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
			pl.append(pack)
		else:
			pl.append(pack)
	if installed:
		for pack in packages:
			if pack not in pl:
				print("Failed to install all dependencies.")
	if installed:
		print("Sucessfully installed all dependencies!")

def _fillblanks(odict, adict):
	return dict(adict, **odict)

def update():
	if args.skip: return
	config = json.load(open(os.path.join("..", "www", "defaultconf.json")))
	try:
		configpage = urllib.request.urlopen(config["update_target"]).read().decode('utf8')
		masterconfig = json.loads(configpage)
		if "version" not in masterconfig: return
		if masterconfig["version"] > config["version"]:
			print("New update found!")
			confirm = ("y" if args.all else "")
			while confirm not in ["y", "n"]:
				confirm = input("Do you want to update from version "+config["version"]+" to "+masterconfig["version"]+"? \n\
This will create a folder LaserQueue-"+masterconfig["version"]+" under "+os.path.abspath(os.path.join("..", ".."))+". \n\
(y / n) ").lower().strip().rstrip()
			if confirm == "y":
				import git
				git.Repo.clone_from(config["update_repo"], os.path.join("..","..","LaserQueue-"+masterconfig["version"]))
				print("New version located in "+os.path.abspath(os.path.join("..","..","LaserQueue-"+masterconfig["version"]))+". Run \n\
"+os.path.abspath(os.path.join("..","..","LaserQueue-"+masterconfig["version"], "start.sh"))+" \n\
to use the new version.\n")

	except Exception as e: 
		print("Error connecting to server: "+str(e))

def main():
	getpacks()
	if args.regen or not os.path.exists(os.path.join("..", "www", "config.json")):
		copyconf()
	if args.host:
		data = json.load(open(os.path.join("..", "www", "config.json")))
		data["host"] = getIps()[0]
		json.dump(data, open(os.path.join("..", "www", "config.json"), "w"), indent=2)
	if args.local:
		data = json.load(open(os.path.join("..", "www", "config.json")))
		data["host"] = "localhost"
		json.dump(data, open(os.path.join("..", "www", "config.json"), "w"), indent=2)
	else:
		data = json.load(open(os.path.join("..", "www", "config.json")))
		if "host" in data and data["host"] == "localhost":
			print("Last time you ran this program, it was in local mode.")
			confirm = ""
			while confirm not in ["y", "n"]:
				confirm = input("Do you want to regenerate the host? (y/n) ").lower().strip().rstrip()
			if confirm == "y":
				data["host"] = getIps()[0]
			json.dump(data, open(os.path.join("..", "www", "config.json"), "w"), indent=2)
	data = json.load(open(os.path.join("..", "www", "config.json")))
	defaultdata = json.load(open(os.path.join("..", "www", "defaultconf.json")))
	if os.path.exists(os.path.join("..", "www", "userconf.json")):
		userdata = json.load(open(os.path.join("..", "www", "userconf.json")))
	else:
		userdata = {}
	defaultdata = _fillblanks(userdata, defaultdata)
	if "host" not in data:
		data["host"] = getIps()[0]
	data = _fillblanks(data, defaultdata)
	data["version"] = defaultdata["version"]
	json.dump(data, open(os.path.join("..", "www", "config.json"), "w"), indent=2)

	update()
				
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