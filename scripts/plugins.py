import sys, os

from config import *
plugprintconf = colorconf()
plugprintconf.color = bcolors.DARKGRAY
plugprintconf.name = "Plugins"

PLUGINDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "plugins"))
sys.path.append(PLUGINDIR)
sys.path.append(os.path.join(os.path.dirname(__file__), "pluginResources"))

def getPlugins():
	cprint("Loading plugins...", colorconfig = plugprintconf)
	pluginFiles = os.listdir(PLUGINDIR)
	pluginPyfiles = filter(lambda x: x.endswith(".py"), pluginFiles)

	def tryImport(name):
		try:
			return __import__(name)
		except Exception as e:
			cprint(tbformat(e, "Error importing {}:".format(name)), color=bcolors.DARKRED, colorconfig = plugprintconf)

	pluginModules = (tryImport(x[:-3]) for x in pluginPyfiles)
	pluginModules = filter(lambda module: (hasattr(module, "upkeep") or hasattr(module, "socketCommands")), pluginModules)
	if pluginModules:
		cprint("Finished loading plugins.", colorconfig = plugprintconf)
	else:
		cprint("No plugins found.", colorconfig = plugprintconf)
	return pluginModules