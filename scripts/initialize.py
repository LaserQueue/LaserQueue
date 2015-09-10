import os, time, pip
import gzip, tarfile
import json, urllib.request, ssl
import getpass, hashlib
from math import ceil

import plugins
from parseargv import args

selfpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(selfpath) # Make sure we're in the correct directory

# Set up pretty printing
from util import *
cprintconf.color = bcolors.CYAN
cprintconf.name = "Setup"

# All the config paths
pluginjspath = os.path.join(os.path.pardir, "www", "dist", "js", "plugins.js")
confpath = os.path.join(os.path.pardir, "www", "config.json")
userconfpath = os.path.join(os.path.pardir, "www", "userconf.json")
defaultconfpath = os.path.join(os.path.pardir, "www", "defaultconf.json")

# Utility function to test for internet connection.
def connected_to_internet():
	return bool(getIps(test=True))

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
	if os.path.exists(confpath) and args.regen != []:
		currdata = openconf()

		if args.regen: # Regenerate everything after -r
			for i in args.regen:
				if i in currdata:
					del currdata[i]

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


def getIps(test=False):
	"""
	Get the IPs this device controls.
	"""
	from netifaces import interfaces, ifaddresses, AF_INET
	ips = []
	for ifaceName in interfaces():
		addresses = [i['addr'] for i in ifaddresses(ifaceName).get(AF_INET, [{"addr":"not found"}])]
		if "not found" not in addresses and "127.0.0.1" not in addresses:
			ips += addresses
	if not ips and not test: 
		ips.append("localhost")
		cprint("WARNING: No internet connection. Using -l behavior.", color=bcolors.YELLOW)
	return ips

def concatJsPlugins():
	js = plugins.getPluginJs()
	concatjs = "\n".join(js)
	with open(pluginjspath, "w") as f:
		f.write(concatjs)


PACKAGES = [
	"websockets",
	"netifaces",
	"GitPython"
]
def getpacks():
	"""
	Go through PACKAGES and install everything missing.
	"""
	if args.skip: 
		cprint("Skipping package install.", color=bcolors.YELLOW)
		return

	# Gets a list of installed packages
	pl = [str(i).split(" ")[0] for i in pip.get_installed_distributions()]

	# Check if anything's been installed
	installed = False

	for pack in PACKAGES:
		if pack in pl:
			continue # Don't do anything if the package is installed
		if not connected_to_internet():
			cprint("No internet connection. Skipping package install.", color=bcolors.YELLOW)
			return
		installed = True

		# Ask if they want to install this dependency
		confirm = ("y" if args.all else "")
		while confirm not in ["y", "n"]:
			confirm = cinput("Install dependency {dep}? (y/n) ", dep=pack).lower().strip()

		if confirm == "n": # If the person chose not to install the dependency
			cprint("WARNING: Program may not run without this library.", color=bcolors.YELLOW)
			continue # Don't do anything
		if pip.main(["install", pack]) and os.name != "nt": # If the install fails and this is a *nix system:
			# Ask again, with minor error colors
			confirm = ("y" if args.all else "")
			while confirm not in ["y", "n"]:
				confirm = cinput("Install failed, try again with elevated permissions? (y/n) ", color=bcolors.RED).lower().strip()

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
				cprint("Failed to install dependency {dep}.", color=bcolors.DARKRED, dep=pack)
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
	if args.skipupdate: 
		cprint("Skipping updating.", color=bcolors.YELLOW)
		return

	if not connected_to_internet():
		cprint("No internet connection. Skipping update.", color=bcolors.YELLOW)
		return

	import git
	config = json.load(open(defaultconfpath))
	ssl._create_default_https_context = ssl.create_default_context

	try:
		configpage = urllib.request.urlopen(config["update_target"]).read().decode('utf8')
		masterconfig = json.loads(configpage) # Get the current up-to-date config

		if "version" in masterconfig and masterconfig["version"] > config["version"]: # If the remote version is greater than the one here

			cprint("New update found: Version {ver}.", ver=masterconfig["version"])

			prefix = format("{path}-", path=os.path.basename(os.path.abspath(os.path.pardir))) # Prefix for new or old versions
			updatedir = os.path.join(os.path.pardir,os.path.pardir,prefix+masterconfig["version"]) # Directory if fetch updating
			backupfile = os.path.join(os.path.pardir, os.path.pardir, prefix+config["version"]+".tar.gz") # Backup file if overwrite updating

			prompt = format("""Do you want to get version {current} to {latest}? 
				                 The fetch option will update into {updatedir}.
				                 The overwrite option will backup to {backupfile}, and fetch master.
				                 (fetch / overwrite / cancel) """, 
				                 current=config["version"], 
				                 lastest=masterconfig["version"], 
				                 updatedir=os.path.abspath(updatedir), 
				                 backupfile=os.path.abspath(backupfile))

			# Check what the user wants to do
			confirm = ("overwrite" if args.allupdate else "")
			while confirm not in ["fetch", "overwrite", "cancel"]:
				confirm = cinput(prompt, strip=True).lower().strip()

			# If they want to fetch the new repository
			if confirm == "fetch":
				git.Repo.clone_from(config["update_repo"], updatedir) # Get the new repository

				# Inform them about it
				cprint("""\nNew version located in: 
				            {updatedir}
				            Run the following: 
				            {startscript} 
				            to use the new version.""",
				            	updatedir=os.path.abspath(updatedir),
				            	startscript=os.path.abspath(os.path.join(updatedir, "start.py")),
				            	strip=True)

			# If they want to overwrite their repository
			elif confirm == "overwrite":
				# Get a git repo object for the folder
				if not os.path.exists(os.path.join(os.path.pardir, ".git")):
					repo = git.Repo.init(os.path.pardir)
				else:
					repo = git.Repo(os.path.pardir)

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
					make_tarfile(backupfile, os.path.pardir)

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
	if args.newpass or not os.path.exists("hashpassword"):
		# Get password
		if args.newpass:
			newpass = cinput("New password: ", func=getpass.getpass)
		else:
			newpass = cinput("Please set the admin login password: ", func=getpass.getpass)

		# Hash the new password
		hash_object = hashlib.sha256(newpass.encode()).hexdigest()
		hashed_final = hashlib.sha256(hash_object.encode()).hexdigest()

		if os.path.exists("hashpassword"):
			# Read the old password
			oldfile = open("hashpassword")
			old = oldfile.read()
			oldfile.close()

			# Make sure we don't overwrite the old password with itself
			if old == hashed_final:
				cprint("Passwords identical. No action taken.")
				return

		try:
			# Write the password to the file
			hashed = open("hashpassword", "w")
			hashed.write(hashed_final)
			hashed.close()
			cprint("Password changed to {starredpass}.", starredpass="*"*len(newpass))
		except Exception as e: # Error reporting
			cprint(tbformat(e, "Error changing password:"), color=bcolors.DARKRED)


def confirmhost():
	"""
	Make sure the config's "host" flag is correct
	"""
	data = openconf()
	# Regenerate the host if -n was used, or if it doesn't exist
	if args.host or "host" not in data and args.regen != []:
		data["host"] = getIps()[0]
	# Change the host to localhost if -l was used (overriding -n)
	if args.local:
		data["host"] = "localhost"
	# Otherwise, reset the host from localhost (ignored by definition if -n is used)
	else:
		if "host" in data and data["host"] == "localhost":
			# Confirm they want to reset the host
			confirm = ""
			while confirm not in ["y", "n"]:
				confirm = cinput("""Last time you ran this program, it was in local mode.
				                    Do you want to regenerate the host? (y/n) """, strip=True).lower().strip()
			# Reset the host if they say yes
			if confirm == "y":
				data["host"] = getIps()[0]
	saveconf(data)



def main():
	"""
	Run all subroutines for initialization.
	"""
	cprint("Beginning initialization.")
	try: getpacks()
	except KeyboardInterrupt: print()
	try: copyconf()
	except KeyboardInterrupt: print()
	try: changepass()	
	except KeyboardInterrupt: print()
	try: confirmhost()
	except KeyboardInterrupt: print()
	try: update()
	except KeyboardInterrupt: print()
	try: concatJsPlugins()
	except KeyboardInterrupt: print()
				
	cprint("Initialization complete.")

if __name__ == "__main__":
	main()