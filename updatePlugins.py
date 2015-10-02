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

PLUGINDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "plugins"))

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

	pluginManifests = list(filter(pluginFilter, pluginManifests))
	if not pluginManifests:
		printer.color_print("No plugin manifests found.")
	return pluginManifests


