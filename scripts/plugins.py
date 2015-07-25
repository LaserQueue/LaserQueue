import sys, os

from config import *
cprintconf.color = bcolors.DARKGRAY
cprintconf.name = "Plugins"

PLUGINDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))
sys.path.append(PLUGINDIR)
sys.path.append(os.path.join(os.path.dirname(__file__), "pluginResources")

def getPlugins():
	pluginFiles = os.listdir(PLUGINDIR)
	pluginPyfiles = filter(lambda x: x.endswith(".py"), pluginFiles)

	def tryImport(name):
		try:
			return __import__(name)
		except Exception as e:
			cprint(tbformat(e, "Error importing {}:".format(name)), color=bcolors.DARKRED)

	pluginModules = (tryImport(x[:-3]) for x in pluginPyfiles)
	pluginModules = filter(lambda module: (hasattr(module, "upkeep") or hasattr(module, "socketCommands")), pluginModules)
	return pluginModules