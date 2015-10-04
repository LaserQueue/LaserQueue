import os, sys

selfpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(selfpath) # Make sure we're in the right directory

if sys.version_info.major < 3 or (sys.version_info.major >= 3 and sys.version_info.minor < 4):
	from cprints import *

	color_printing_config.color = ansi_colors.DARKRED
	color_printing_config.name = "Error"
	version = sys.version.split(" ")[0]

	color_print("""The version of Python is outdated.
		Found: {version}
		Required: 3.4+
		Please update to the correct version.""",
		version=version, 
		color=ansi_colors.DARKRED, strip=True)
	quit()

import pip, argparse, git

PLUGINDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "plugins"))

def fetch_dependencies(packs):
	"""
	Go through packs and install everything missing.
	"""
	if args.skip: 
		color_print("Skipping package install.", color=ansi_colors.YELLOW)
		return
	# Gets a list of installed packages
	installed_packages = [str(i).split(" ")[0] for i in pip.get_installed_distributions()]

	# Check if anything's been installed
	installed = False

	for package in packs:
		if package in installed_packages:
			continue # Don't do anything if the package is installed
		if "netifaces" in installed_packages and not connected_to_internet():
			color_print("No internet connection. Skipping package install.", color=ansi_colors.YELLOW)
			return
		installed = True

		# Ask if they want to install this dependency
		confirm = ("y" if args.all else "")
		while confirm not in ["y", "n"]:
			confirm = color_input("Install dependency {dep}? (y/n) ", dep=package).lower().strip()

		if confirm == "n": # If the person chose not to install the dependency
			color_print("WARNING: Program may not run without this library.", color=ansi_colors.YELLOW)
			continue # Don't do anything
		if pip.main(["install", package]) and os.name != "nt": # If the install fails and this is a *nix system:
			# Ask again, with minor error colors
			confirm = ("y" if args.all else "")
			while confirm not in ["y", "n"]:
				confirm = color_input("Install failed, try again with elevated permissions? (y/n) ", color=ansi_colors.RED).lower().strip()

			if confirm == "n": # If the person chose not to install the dependency
				color_print("WARNING: Program may not run without this library.", color=ansi_colors.YELLOW)
				continue # Don't do anything
			if not os.system("sudo pip3 install "+package): # Try again with root permissions
				installed_packages.append(package) # If it succeeds, add it to the installed packages
		else:
			installed_packages.append(package) # If it succeeds at first, add it to the installed packages
	if installed:
		for package in packs:
			if package not in installed_packages:
				color_print("Failed to install dependency {dep}.", color=ansi_colors.DARKRED, dep=package)
				installed = False # If not everything's been installed, don't say it was successful

	if installed:
		color_print("Sucessfully installed all dependencies!")

# Allow importing from scripts
sys.path.append(
	os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))
from util import *
color_printing_config.color = ansi_colors.DARKGRAY
color_printing_config.name = "Plugins"


def tryLoadManifest(folder, name):
	try:
		with open(os.path.join(folder, name)) as f:
			return json.load(f)
	except Exception as e:
		color_print(format_traceback(e, format("Error loading {name}'s manifest:", name=folder)), color=ansi_colors.DARKRED)

def hasManifest(filename):
	subFiles = os.listdir(os.path.join(PLUGINDIR, filename))
	acceptableFiles = filter(lambda x: x.lower() == "manifest.json", subFiles)
	return bool(list(acceptableFiles))

def getManifests():
	plugins = os.listdir(PLUGINDIR)
	pluginFolders = filter(lambda filename: os.path.isdir(os.path.join(PLUGINDIR, filename)), plugins)
	pluginManifested = filter(hasManifest, pluginFolders)

	pluginManifests = []

	for i in pluginManifested:
		pluginFiles = os.listdir(os.path.join(PLUGINDIR, i))
		pluginFiles = filter(lambda filename: x.lower() == "manifest.json", pluginFiles)
		for j in pluginFiles:
			imported = tryLoadManifest(i, j)
			pluginManifests.append(imported)
			break

	if not pluginManifests:
		color_print("No plugin manifests found.")
	return pluginManifests


if __name__ == "__main__":
	parser = argparse.ArgumentParser(add_help=False, usage="%(prog)s [options]",)
	parser.add_argument("-f", "--fetch", help="Pull from plugins.json and install", dest="fetch",
		action="store_true")
	parser.add_argument("-h", "--help", help="Show this help message and exit", action="help")
	args = parser.parse_args()

	pluginFolders = list(filter(lambda filename: os.path.isdir(os.path.join(PLUGINDIR, filename)), os.listdir(PLUGINDIR)))
	if args.fetch:
		plugins = Config("plugins.json")
		for pl in plugins:
			if pl['name'] not in pluginFolders:
				git.Repo.clone_from(pl['target'], os.path.join(PLUGINDIR, pl['name']))
	else:
		manifests = getManifests()
		pass
		



