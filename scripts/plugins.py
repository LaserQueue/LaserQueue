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
		return __import__(name)
	except Exception as e:
		printer.cprint(tbformat(e, "Error importing {}:".format(name)), color=bcolors.DARKRED)

def pluginFilter(module):
	return (hasattr(module, "upkeep") or
		hasattr(module, "socketCommands"))

def getPlugins():
	if args.noPlugins:
		printer.cprint("Skipping plugin load.")
		return []
	printer.cprint("Loading plugins...")
	pluginFiles = os.listdir(PLUGINDIR)
	pluginPyfiles = filter(lambda x: x.endswith(".py"), pluginFiles)

	pluginModules = (tryImport(x[:-3]) for x in pluginPyfiles)
	pluginModules = filter(pluginFilter, pluginModules)
	if list(pluginModules):
		printer.cprint("Finished loading plugins.")
	else:
		printer.cprint("No plugins found.")
	return pluginModules