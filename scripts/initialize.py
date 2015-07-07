import json
import os
import socket
import pip
import argparse
import gzip
import urllib.request
import tarfile
import time
from math import ceil

from parseargv import args

import ssl
if hasattr(ssl, '_create_unverified_context'): 
    ssl._create_default_https_context = ssl._create_unverified_context

selfpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(selfpath)

from config import *
cprintconf.color = bcolors.CYAN
cprintconf.name = "Setup"

def qsort(l):
		if l == []: 
				return []
		else:
				pivot = l[0]
				lesser = qsort([x for x in l[1:] if x < pivot])
				greater = qsort([x for x in l[1:] if x >= pivot])
				return lesser + [pivot] + greater

def copyconf(dataoverride = False):
	if os.path.exists(os.path.join("..", "www", "config.json")) and not dataoverride:
		currdata = json.load(open(os.path.join("..", "www", "config.json")))
		if "host" not in currdata or not currdata["host"]:
			currdata["host"] = getIps()[0]
	else:
		currdata = {"host": getIps()[0]}
	data = json.load(open(os.path.join("..", "www", "defaultconf.json")))
	if os.path.exists(os.path.join("..", "www", "userconf.json")):
		userdata = json.load(open(os.path.join("..", "www", "userconf.json")))
	else:
		userdata = {}
	data = dict(currdata, **dict(data, **userdata))
	json.dump(data, open(os.path.join("..", "www", "config.json"), "w"), indent=2)

PACKAGES = [
	"websockets",
	"netifaces",
	"GitPython"
]
def getpacks():
	if args.skip: return
	pl = [str(i).split(" ")[0] for i in pip.get_installed_distributions()]
	installed = False
	for pack in PACKAGES:
		if pack in pl:
			continue
		installed = True
		confirm = ("y" if args.all else "")
		while confirm not in ["y", "n"]:
			confirm = cinput("Install dependency "+pack+"? (y/n) ").lower().strip().rstrip()
		if confirm == "n": 
			cprint(bcolors.YELLOW + "WARNING: Program may not run without this library.")
			continue
		if pip.main(["install", pack]) and os.name != "nt":
			confirm = ("y" if args.all else "")
			while confirm not in ["y", "n"]:
				confirm = cinput(bcolors.RED + "Install failed, try again with elevated permissions? (y/n) ").lower().strip().rstrip()
			if confirm == "n": 
				cprint(bcolors.YELLOW + "WARNING: Program may not run without this library.")
				continue
			if not os.system("sudo pip3 install "+pack):
				pl.append(pack)
		else:
			pl.append(pack)
	if installed:
		for pack in PACKAGES:
			if pack not in pl:
				cprint(bcolors.DARKRED + "Failed to install dependency "+pack+".")
				installed = False
	if installed:
		cprint("Sucessfully installed all dependencies!")

def _fillblanks(odict, adict):
	return dict(adict, **odict)

def make_tarfile(output_filename, source_dir):
		with tarfile.open(output_filename, "w:gz") as tar:
				tar.add(source_dir, arcname=os.path.basename(source_dir))

def update():
	if args.skipupdate: return
	config = json.load(open(os.path.join("..", "www", "defaultconf.json")))


	try:
		configpage = urllib.request.urlopen(config["update_target"]).read().decode('utf8')
		masterconfig = json.loads(configpage)
		if "version" not in masterconfig: return
		if masterconfig["version"] > config["version"]:
			cprint("New update found: Version "+masterconfig["version"]+".")
			confirm = ("overwrite" if args.allupdate else "")
			prefix = os.path.basename(os.path.abspath(".."))+"-"

			while confirm not in ["fetch", "overwrite", "cancel"]:
				confirm = cinput("Do you want to get version "+config["version"]+" to "+masterconfig["version"]+"? \n\
The fetch option will update into "+os.path.abspath(os.path.join("..", "..", prefix+masterconfig["version"]))+". \n\
The overwrite option will backup to "+os.path.abspath(os.path.join("..", "..", prefix+config["version"]+".tar.gz"))+", and fetch master. \n\
(fetch / overwrite / cancel) ").lower().strip().rstrip()
			import git
			if confirm == "fetch":
				git.Repo.clone_from(config["update_repo"], os.path.join("..","..",prefix+masterconfig["version"]))

				cprint("\nNew version located in "+os.path.abspath(os.path.join("..","..",prefix+masterconfig["version"]))+". Run \n\
"+os.path.abspath(os.path.join("..","..",prefix+masterconfig["version"], "start.py"))+" \n\
to use the new version.\n")
			elif confirm == "overwrite":
				if not os.path.exists(os.path.join("..", ".git")):
					repo = git.Repo.init("..")
				else:
					repo = git.Repo("..")
				if "origin" not in [i.name for i in repo.remotes]:
					origin = repo.create_remote("origin", config["update_repo"])
					origin.fetch()
				try:
					tarchive = open(os.path.join("..", "..", prefix+config["version"]+".tar.gz"), 'wb')
					repo.archive(tarchive)
					gzip.GzipFile(fileobj=tarchive, mode='wb')
				except:
					make_tarfile(os.path.join("..", "..", prefix+config["version"]+".tar.gz"), "..")

				repo.git.fetch("--all")
				repo.git.reset("--hard", "origin/master")
				json.dump(config, open(os.path.join("..", "www", "config.json"), "w"))

				quit(10)
	except Exception as e: 
		cprint(bcolors.DARKRED + "Error updating: "+str(e))

def main():
	getpacks()
	if args.regen:
		copyconf(True)
	else:
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
			cprint("Last time you ran this program, it was in local mode.")
			confirm = ""
			while confirm not in ["y", "n"]:
				confirm = cinput("Do you want to regenerate the host? (y/n) ").lower().strip().rstrip()
			if confirm == "y":
				data["host"] = getIps()[0]
			json.dump(data, open(os.path.join("..", "www", "config.json"), "w"), indent=2)
	data = json.load(open(os.path.join("..", "www", "config.json")))
	defaultdata = json.load(open(os.path.join("..", "www", "defaultconf.json")))
	if "host" not in data:
		data["host"] = getIps()[0]
	data["version"] = defaultdata["version"]
	json.dump(data, open(os.path.join("..", "www", "config.json"), "w"), indent=2)

	update()
				
	cprint("Initialization complete.")

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