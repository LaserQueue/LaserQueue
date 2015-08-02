import sys, os
from parseargv import args
from pluginResources.QueueConfig import *
printer = PluginPrinterInstance()
printer.setcolor(bcolors.DARKGRAY)
printer.setname("Plugins")

PLUGINDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "plugins"))
sys.path.append(PLUGINDIR)
sys.path.append(os.path.join(os.path.dirname(__file__), "pluginResources"))

def tryImport(name):
	try:
		if args.loud:
			printer.cprint("Loading {}...".format(name))
		imported =  __import__(name)
		if args.loud:
			if pluginFilter(imported):
				printer.cprint("{} successfully loaded.".format(name))
			else:
				printer.cprint("{} not a plugin.".format(name))
		return imported
	except Exception as e:
		printer.cprint(tbformat(e, "Error importing {}:".format(name)), color=bcolors.DARKRED)

def tryLoadJS(folder, name):
	try:
		with open(os.path.join(folder, name)) as f:
			return f.read().strip().rstrip().strip("\n").rstrip("\n").strip().rstrip()
	except Exception as e:
		printer.cprint(tbformat(e, "Error loading {}:".format(name)), color=bcolors.DARKRED)


def pluginFilter(module):
	return (hasattr(module, "upkeep") or
		hasattr(module, "socketCommands") or
		hasattr(module, "hideFromClient") or
		hasattr(module, "requiredTags") or
		hasattr(module, "requiresAuth"))

def hasPy(filename):
	subFiles = os.listdir(os.path.join(PLUGINDIR, filename))
	acceptableFiles = filter(lambda x: x.endswith(".py"), subFiles)
	return bool(list(acceptableFiles))
def hasJs(filename):
	subFiles = os.listdir(os.path.join(PLUGINDIR, filename))
	acceptableFiles = filter(lambda x: x.endswith(".js"), subFiles)
	return bool(list(acceptableFiles))


def getPlugins():
	if args.noPlugins:
		return []
	printer.cprint("Loading Python plugins...")
	plugins = os.listdir(PLUGINDIR)
	pluginFolders = filter(lambda filename: os.path.isdir(os.path.join(PLUGINDIR, filename)), plugins)
	pluginsPy = filter(hasPy, pluginFolders)

	pluginModules = []

	for i in pluginsPy:
		pluginPyFiles = os.listdir(os.path.join(PLUGINDIR, i))
		pluginPyFiles = filter(lambda filename: filename.endswith(".py"), pluginPyFiles)
		sys.path.append(os.path.join(PLUGINDIR, i))
		for j in pluginPyFiles:
			imported = tryImport(j[:-3])
			pluginModules.append(imported)

	pluginModules = filter(pluginFilter, pluginModules)
	if pluginModules:
		printer.cprint("Finished loading Python plugins.")
	else:
		printer.cprint("No Python plugins found.")
	return pluginModules



def getPluginJs():
	if args.noPlugins:
		return []
	printer.cprint("Loading JS plugins...")
	plugins = os.listdir(PLUGINDIR)
	pluginFolders = filter(lambda filename: os.path.isdir(os.path.join(PLUGINDIR, filename)), plugins)
	pluginsJs = filter(hasJs, pluginFolders)

	pluginJs = []

	for i in pluginsJs:
		pluginJsFiles = os.listdir(os.path.join(PLUGINDIR, i))
		pluginJsFiles = filter(lambda filename: filename.endswith(".js"), pluginJsFiles)
		for j in pluginJsFiles:
			pluginModules.append(tryLoadJs(i, j))

	if pluginJs:
		printer.cprint("Finished loading JS plugins.")
	else:
		printer.cprint("No JS plugins found.")
	return pluginJs
