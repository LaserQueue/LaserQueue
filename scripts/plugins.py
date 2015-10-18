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

def tryLoadFile(folder, name):
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
	hasattr(module, "requiresAuth") or
	hasattr(module, "eventRegistry"))

def hasPy(filename):
	subFiles = os.listdir(os.path.join(PLUGINDIR, filename))
	acceptableFiles = filter(lambda x: x.endswith(".py"), subFiles)
	return bool(list(acceptableFiles))
def hasftypeFactory(ftype):
	def hasftype(filename):
		subFiles = os.listdir(os.path.join(PLUGINDIR, filename))
		acceptableFiles = filter(lambda x: x.endswith(ftype), subFiles)
		return bool(list(acceptableFiles))
	return hasftype


def getPlugins():
	if args.noPlugins:
		return []
	if args.loud:
		printer.color_print("Loading Python plugins...")
	reg = Registry()
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
			if imported:
				if hasattr(imported, "eventRegistry"):
					if isinstance(imported.eventRegistry, Registry):
						reg.graft(imported.eventRegistry)
					else:
						printer.color_print("{name}.eventRegistry isn't a Registry!", name=j[:-3], color=ansi_colors.DARKRED)
				pluginModules.append(imported)

	pluginModules = list(filter(pluginFilter, pluginModules))
	if args.loud:
		if pluginModules:
			printer.color_print("Finished loading Python plugins.")
		else:
			printer.color_print("No Python plugins found.")
	return pluginModules, reg



def getPluginFiletype(ftype):
	if args.noPlugins:
		return []
	if args.loud:
		printer.color_print("Loading {type} plugins...", type=ftype)
	plugins = os.listdir(PLUGINDIR)
	pluginFolders = filter(lambda filename: os.path.isdir(os.path.join(PLUGINDIR, filename)), plugins)
	plugins = filter(hasftypeFactory(ftype), pluginFolders)

	plugin = []

	for i in plugins:
		pluginFiles = os.listdir(os.path.join(PLUGINDIR, i))
		pluginFiles = filter(lambda filename: filename.endswith(ftype), pluginFiles)
		for j in pluginFiles:
			plugin.append(tryLoadFile(i, j))

	plugin = list(filter(lambda x: x, plugin))

	if args.loud:
		if plugin:
			printer.color_print("Finished loading {type} plugins.", type=ftype)
		else:
			printer.color_print("No {type} plugins found.", type=ftype)
	return plugin
