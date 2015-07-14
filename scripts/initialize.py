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
if hasattr(ssl, '_create_unverified_context'): # Some operating systems don't have the default https context.
    ssl._create_default_https_context = ssl._create_unverified_context

selfpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(selfpath) # Make sure we're in the correct directory

# Set up pretty printing
from config import *
cprintconf.color = bcolors.CYAN
cprintconf.name = "Setup"

# All the config paths
confpath = os.path.join("..", "www", "config.json")
userconfpath = os.path.join("..", "www", "userconf.json")
defaultconfpath = os.path.join("..", "www", "defaultconf.json")

# Config functions
def openconf():
	"""
	Opens the config file and returns its contents.
	"""
	return json.load(open(confpath))

def saveconf(data):
	"""
	Saves `data` to the config file.
	"""
	return json.dump(data, open(confpath, "w"), indent=2, sort_keys=True)

def copyconf():
	"""
	Make sure the config has the required data in it.
	If args.regen, it will pretend as though the original config was empty.
	"""
	if os.path.exists(confpath) and not args.regen:
		currdata = openconf()
		if "host" not in currdata or not currdata["host"]:
			currdata["host"] = getIps()[0]
		if "version" in currdata: # Version should always be latest
			del currdata["version"]
	else:
		currdata = {"host": getIps()[0]}
	data = json.load(open(defaultconfpath))
	if os.path.exists(userconfpath):
		userdata = json.load(open(userconfpath))
	else:
		userdata = {}
	data = dict(dict(data, **userdata), **currdata)
	saveconf(data)


def getIps():
	"""
	Get the IPs this device controls.
	"""
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
	"""
	Go through PACKAGES and install everything missing.
	"""
	if args.skip: return

	# Gets a list of installed packages
	pl = [str(i).split(" ")[0] for i in pip.get_installed_distributions()]

	# Check if anything's been installed
	installed = False

	for pack in PACKAGES:
		if pack in pl:
			continue # Don't do anything if the package is installed
		installed = True

		# Ask if they want to install this dependency
		confirm = ("y" if args.all else "")
		while confirm not in ["y", "n"]:
			confirm = cinput("Install dependency "+pack+"? (y/n) ").lower().strip().rstrip()

		if confirm == "n": # If the person chose not to install the dependency
			cprint("WARNING: Program may not run without this library.", color=bcolors.YELLOW)
			continue # Don't do anything
		if pip.main(["install", pack]) and os.name != "nt": # If the install fails and this is a *nix system:
			# Ask again, with minor error colors
			confirm = ("y" if args.all else "")
			while confirm not in ["y", "n"]:
				confirm = cinput("Install failed, try again with elevated permissions? (y/n) ", color=bcolors.RED).lower().strip().rstrip()

			if confirm == "n": # If the person chose not to install the dependency
				cprint("WARNING: Program may not run without this library.", color=bcolors.YELLOW)
				continue # Don't do anything
			if not os.system("sudo pip3 install "+pack): # Try again with root permissions
				pl.append(pack) # If it succeeds, add it to the installed packages
		else:
			pl.append(pack) # If it succeeds at first, add it to the installed packages
	if installed:
		for pack in PACKAGES:
			if pack not in pl:
				cprint("Failed to install dependency "+pack+".", color=bcolors.DARKRED)
				installed = False # If not everything's been installed, don't say it was successful

	if installed:
		cprint("Sucessfully installed all dependencies!")




def _fillblanks(odict, adict):
	"""
	Merge the dictionary odict over the dictionary adict.
	"""
	return dict(adict, **odict) 

def make_tarfile(output_filename, source_dir):
	"""
	Make a tarball of the chosen directory to the chosen filename.
	"""
	with tarfile.open(output_filename, "w:gz") as tar:
			tar.add(source_dir, arcname=os.path.basename(source_dir))

def update():
	"""
	Try to update LaserQueue to the latest version.
	"""
	if args.skipupdate: return

	import git
	config = json.load(open(defaultconfpath))

	try:
		configpage = urllib.request.urlopen(config["update_target"]).read().decode('utf8')
		masterconfig = json.loads(configpage) # Get the current up-to-date config

		if "version" in masterconfig and masterconfig["version"] > config["version"]: # If the remote version is greater than the one here

			cprint("New update found: Version {}.".format(masterconfig["version"]))

			prefix = "{}-".format(os.path.basename(os.path.abspath(".."))) # Prefix for new or old versions
			updatedir = os.path.join("..","..",prefix+masterconfig["version"]) # Directory if fetch updating
			backupfile = os.path.join("..", "..", prefix+config["version"]+".tar.gz") # Backup file if overwrite updating

			prompt = """Do you want to get version {} to {}? 
				          The fetch option will update into {}.
				          The overwrite option will backup to {}, and fetch master.
				          (fetch / overwrite / cancel) """.format(config["version"], masterconfig["version"], 
				          	os.path.abspath(updatedir), os.path.abspath(backupfile))

			# Check what the user wants to do
			confirm = ("overwrite" if args.allupdate else "")
			while confirm not in ["fetch", "overwrite", "cancel"]:
				confirm = cinput(prompt, strip=True).lower().strip().rstrip()

			# If they want to fetch the new repository
			if confirm == "fetch":
				git.Repo.clone_from(config["update_repo"], updatedir) # Get the new repository

				# Inform them about it
				cprint("""\nNew version located in: 
				            {}
				            Run the following: 
				            {} 
				            to use the new version.""".format(
				            	os.path.abspath(updatedir),
				            	os.path.abspath(os.path.join(updatedir, "start.py"))
				            ), strip=True)

			# If they want to overwrite their repository
			elif confirm == "overwrite":
				# Get a git repo object for the folder
				if not os.path.exists(os.path.join("..", ".git")):
					repo = git.Repo.init("..")
				else:
					repo = git.Repo("..")

				# If the repo doesn't have a connection to the remote, make one
				if "origin" not in [i.name for i in repo.remotes]:
					origin = repo.create_remote("origin", config["update_repo"])
					origin.fetch()

				# Make a backup file
				try:
					tarchive = open(backupfile, 'wb')
					repo.archive(tarchive)
					gzip.GzipFile(fileobj=tarchive, mode='wb')
				except:
					make_tarfile(backupfile, "..")

				# Reset the repository
				repo.git.fetch("--all")
				repo.git.reset("--hard", "origin/master")
				json.dump(config, open(confpath, "w"), sort_keys=True)
				quit(10) # Tells the start script to restart
	except Exception as e: # Error reporting
		cprint(tbformat(e, "Error updating:"), color=bcolors.DARKRED)



def changepass():
	"""
	Change the password if --new-password used.
	"""
	if args.newpass:
		# Get password
		newpass = cinput("New password: ", func=getpass.getpass)

		try:
			# Hash the new password
			hash_object = hashlib.sha256(newpass.encode()).hexdigest()
			hashed_final = hashlib.sha256(hash_object.encode()).hexdigest()

			# Read the old password
			oldfile = open("hashpassword")
			old = oldfile.read()
			oldfile.close()

			# Make sure we don't overwrite the old password with itself
			if old == hashed_final:
				cprint("Passwords identical. No action taken.")
				return

			# Write the password to the file
			hashed = open("hashpassword", "w")
			hashed.write(hashed_final)
			hashed.close()
			cprint("Password changed to {}.".format("*"*len(newpass)))
		except Exception as e: # Error reporting
			cprint(tbformat(e, "Error changing password:"), color=bcolors.DARKRED)


def confirmhost():
	"""
	Make sure the config's "host" flag is correct
	"""
	data = openconf()
	# Regenerate the host if -n was used, or if it doesn't exist
	if args.host or "host" not in data:
		data["host"] = getIps()[0]
	# Change the host to localhost if -l was used (overriding -n)
	if args.local:
		data["host"] = "localhost"
	# Otherwise, reset the host from localhost (ignored by definition if -n is used)
	else:
		if "host" in data and data["host"] == "localhost":
			cprint("")

			# Confirm they want to reset the host
			confirm = ""
			while confirm not in ["y", "n"]:
				confirm = cinput("""Last time you ran this program, it was in local mode.
				                    Do you want to regenerate the host? (y/n) """, strip=True).lower().strip().rstrip()
			# Reset the host if they say yes
			if confirm == "y":
				data["host"] = getIps()[0]
	saveconf(data)



def main():
	"""
	Run all subroutines for initialization.
	"""
	cprint("Beginning initialization.")

	getpacks()
	copyconf()
	changepass()	
	confirmhost()
	update()
				
	cprint("Initialization complete.")

if __name__ == "__main__":
	main()