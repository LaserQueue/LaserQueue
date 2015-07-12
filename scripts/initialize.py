import json
import os
import socket
import pip
import argparse
import gzip
import urllib.request
import tarfile
import time
import getpass, hashlib
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


confpath = os.path.join("..", "www", "config.json")
uconfpath = os.path.join("..", "www", "userconf.json")
dconfpath = os.path.join("..", "www", "defaultconf.json")


def openconf():
	return json.load(open(confpath))

def saveconf(data):
	return json.dump(data, open(confpath, "w"), indent=2, sort_keys=True)

def copyconf():
	if os.path.exists(confpath) and not args.regen:
		currdata = openconf()
		if "host" not in currdata or not currdata["host"]:
			currdata["host"] = getIps()[0]
	else:
		currdata = {"host": getIps()[0]}
	data = json.load(open(dconfpath))
	if os.path.exists(uconfpath):
		userdata = json.load(open(uconfpath))
	else:
		userdata = {}
	data = dict(dict(data, **userdata), **currdata)
	saveconf(data)


def getIps():
	from netifaces import interfaces, ifaddresses, AF_INET
	ips = []
	for ifaceName in interfaces():
		addresses = [i['addr'] for i in ifaddresses(ifaceName).get(AF_INET, [{"addr":"not found"}])]
		if "not found" not in addresses and "127.0.0.1" not in addresses:
			ips += addresses
	return ips


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
			cprint("WARNING: Program may not run without this library.", color=bcolors.YELLOW)
			continue
		if pip.main(["install", pack]) and os.name != "nt":
			confirm = ("y" if args.all else "")
			while confirm not in ["y", "n"]:
				confirm = cinput( + "Install failed, try again with elevated permissions? (y/n) ", color=bcolors.RED).lower().strip().rstrip()
			if confirm == "n": 
				cprint("WARNING: Program may not run without this library.", color=bcolors.YELLOW)
				continue
			if not os.system("sudo pip3 install "+pack):
				pl.append(pack)
		else:
			pl.append(pack)
	if installed:
		for pack in PACKAGES:
			if pack not in pl:
				cprint("Failed to install dependency "+pack+".", color=bcolors.DARKRED)
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
	import git
	config = json.load(open(dconfpath))

	try:
		configpage = urllib.request.urlopen(config["update_target"]).read().decode('utf8')
		masterconfig = json.loads(configpage)

		if "version" in masterconfig and masterconfig["version"] > config["version"]:

			cprint("New update found: Version {}.".format(masterconfig["version"]))

			prefix = "{}-".format(os.path.basename(os.path.abspath("..")))
			updatedir = os.path.join("..","..",prefix+masterconfig["version"])
			backupfile = os.path.join("..", "..", prefix+config["version"]+".tar.gz")

			prompt = """Do you want to get version {} to {}? 
				          The fetch option will update into {}.
				          The overwrite option will backup to {}, and fetch master.
				          (fetch / overwrite / cancel) """.format(config["version"], masterconfig["version"], 
				          	os.path.abspath(updatedir), os.path.abspath(backupfile))

			confirm = ("overwrite" if args.allupdate else "")
			while confirm not in ["fetch", "overwrite", "cancel"]:
				confirm = cinput(prompt, strip=True).lower().strip().rstrip()

			if confirm == "fetch":
				git.Repo.clone_from(config["update_repo"], updatedir)

				cprint("""\nNew version located in: 
				            {}
				            Run the following: 
				            {} 
				            to use the new version.""".format(
				            	os.path.abspath(updatedir),
				            	os.path.abspath(os.path.join(updatedir, "start.py"))
				            ), strip=True)

			elif confirm == "overwrite":
				if not os.path.exists(os.path.join("..", ".git")):
					repo = git.Repo.init("..")
				else:
					repo = git.Repo("..")
				if "origin" not in [i.name for i in repo.remotes]:
					origin = repo.create_remote("origin", config["update_repo"])
					origin.fetch()
				try:
					tarchive = open(backupfile, 'wb')
					repo.archive(tarchive)
					gzip.GzipFile(fileobj=tarchive, mode='wb')
				except:
					make_tarfile(backupfile, "..")

				repo.git.fetch("--all")
				repo.git.reset("--hard", "origin/master")
				json.dump(config, open(confpath, "w"), sort_keys=True)
				quit(10) # Tells the start script to restart
	except Exception as e: 
		cprint(tbformat(e, "Error updating:"), color=bcolors.DARKRED)



def changepass():
	if type(args.newpass) is bool:
		newpass = cinput("New password: ", func=getpass.getpass)
	else:
		newpass = args.newpass
	try:
		hash_object = hashlib.sha256(newpass.encode()).hexdigest()
		hashed_final = hashlib.sha256(hash_object.encode()).hexdigest()
		hashed = open("hashpassword", "w")
		hashed.write(hashed_final)
		hashed.close()
		cprint("Password changed to {}.".format("*"*len(newpass)))
	except Exception as e:
		cprint(tbformat(e, "Error changing password:"), color=bcolors.DARKRED)


def confirmhost():
	if args.host:
		data = openconf()
		data["host"] = getIps()[0]
		saveconf(data)
	if args.local:
		data = openconf()
		data["host"] = "localhost"
		saveconf(data)
	else:
		data = openconf()
		if "host" in data and data["host"] == "localhost":
			cprint("Last time you ran this program, it was in local mode.")

			confirm = ""
			while confirm not in ["y", "n"]:
				confirm = cinput("Do you want to regenerate the host? (y/n) ").lower().strip().rstrip()

			if confirm == "y":
				data["host"] = getIps()[0]
			saveconf(data)

	data = openconf()
	defaultdata = json.load(open(dconfpath))
	if "host" not in data:
		data["host"] = getIps()[0]
	data["version"] = defaultdata["version"]
	saveconf(data)



def main():
	getpacks()
	copyconf()
	if args.newpass: changepass()	
	confirmhost()
	update()
				
	cprint("Initialization complete.")

if __name__ == "__main__":
	main()