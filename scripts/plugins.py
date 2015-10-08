from parseargv import args
from pluginResources.QueueConfig import *
printer = PluginPrinterInstance(ansi_colors.DARKGRAY, "Plugins")

PLUGINDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "plugins"))
sys.path.append(PLUGINDIR)
sys.path.append(os.path.join(os.path.dirname(__file__), "pluginResources"))

def tryImport(name):
	try:
		if args.loud:
			printer.color_print("Loading {name}...", name=name)
		imported =  __import__(name)
		if args.loud:
			if pluginFilter(imported):
				printer.color_print("{name} successfully loaded.", name=name)
			else:
				printer.color_print("{name} not a plugin.", name=name)
		return imported
	except Exception as e:
		printer.color_print(format_traceback(e, format("Error importing {name}:", name=name)), color=ansi_colors.DARKRED)

def tryLoadJS(folder, name):
	try:
		with open(os.path.join(os.path.pardir, 'plugins', folder, name)) as f:
			return f.read().strip()
	except Exception as e:
		printer.color_print(format_traceback(e, format("Error loading {name}:", name=name)), color=ansi_colors.DARKRED)


pluginFilter = lambda module: (
	hasattr(module, "upkeep") or
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
	printer.color_print("Loading Python plugins...")
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

	pluginModules = list(filter(pluginFilter, pluginModules))
	if pluginModules:
		printer.color_print("Finished loading Python plugins.")
	else:
		printer.color_print("No Python plugins found.")
	return pluginModules



def getPluginJs():
	if args.noPlugins:
		return []
	printer.color_print("Loading JS plugins...")
	plugins = os.listdir(PLUGINDIR)
	pluginFolders = filter(lambda filename: os.path.isdir(os.path.join(PLUGINDIR, filename)), plugins)
	pluginsJs = filter(hasJs, pluginFolders)

	pluginJs = []

	for i in pluginsJs:
		pluginJsFiles = os.listdir(os.path.join(PLUGINDIR, i))
		pluginJsFiles = filter(lambda filename: filename.endswith(".min.js"), pluginJsFiles)
		for j in pluginJsFiles:
			pluginJs.append(tryLoadJS(i, j))

	pluginJs = list(filter(lambda x: x, pluginJs))

	if pluginJs:
		printer.color_print("Finished loading JS plugins.")
	else:
		printer.color_print("No JS plugins found.")
	return pluginJs
