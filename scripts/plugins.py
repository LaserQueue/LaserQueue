from parseargv import args
from pluginResources.QueueConfig import *
printer = Printer(ansi_colors.DARKGRAY, "Plugins")

selfpath = os.path.dirname(__file__)

PLUGINDIR = os.path.abspath(os.path.join(selfpath, os.path.pardir, "plugins"))
sys.path.append(PLUGINDIR)
sys.path.append(os.path.join(selfpath, "pluginResources"))

def try_import(name):
	try:
		if args.loud:
			printer.color_print("Loading {name}...", name=name)
		imported = __import__(name)
		if args.loud:
			if pluginFilter(imported):
				printer.color_print("{name} successfully loaded.", name=name)
			else:
				printer.color_print("{name} not a plugin.", name=name)
		return imported
	except Exception as e:
		printer.color_print(format_traceback(e, format("Error importing {name}:", name=name)), color=ansi_colors.DARKRED)

def try_load_file(folder, name):
	try:
		with open(os.path.join(selfpath, os.path.pardir, 'plugins', folder, name)) as f:
			return f.read().strip()
	except Exception as e:
		printer.color_print(format_traceback(e, format("Error loading {name}:", name=name)), color=ansi_colors.DARKRED)


pluginFilter = lambda module: (hasattr(module, "registry"))

def has_py(filename):
	subFiles = os.listdir(os.path.join(PLUGINDIR, filename))
	acceptableFiles = filter(lambda x: x.endswith(".py"), subFiles)
	return bool(list(acceptableFiles))
def has_filetype_factory(ftype):
	def has_filetype(filename):
		subFiles = os.listdir(os.path.join(PLUGINDIR, filename))
		acceptableFiles = filter(lambda x: x.endswith(ftype), subFiles)
		return bool(list(acceptableFiles))
	return has_filetype


def getPlugins():
	if args.no_plugins:
		return Registry()
	if args.loud:
		printer.color_print("Loading Python plugins...")
	reg = Registry()
	plugins = os.listdir(PLUGINDIR)
	plugin_folders = filter(lambda filename: os.path.isdir(os.path.join(PLUGINDIR, filename)), plugins)
	plugins_py = filter(has_py, plugin_folders)

	plugin_modules = []

	for i in plugins_py:
		plugin_py_files = os.listdir(os.path.join(PLUGINDIR, i))
		plugin_py_files = filter(lambda filename: filename.endswith(".py"), plugin_py_files)
		sys.path.append(os.path.join(PLUGINDIR, i))
		for j in plugin_py_files:
			imported = try_import(j[:-3])
			if imported:
				if hasattr(imported, "registry"):
					if isinstance(imported.registry, Registry):
						reg.graft(imported.registry)
					else:
						printer.color_print("{name}.registry isn't a Registry!", name=j[:-3], color=ansi_colors.DARKRED)
				plugin_modules.append(imported)

	plugin_modules = list(filter(pluginFilter, plugin_modules))
	if args.loud:
		if plugin_modules:
			printer.color_print("Finished loading Python plugins.")
		else:
			printer.color_print("No Python plugins found.")
	return reg



def get_plugin_filetype(ftype):
	if args.no_plugins:
		return []
	if args.loud:
		printer.color_print("Loading {type} plugins...", type=ftype)
	plugins = os.listdir(PLUGINDIR)
	plugin_folders = filter(lambda filename: os.path.isdir(os.path.join(PLUGINDIR, filename)), plugins)
	plugins = filter(has_filetype_factory(ftype), plugin_folders)

	plugin = []

	for i in plugins:
		plugin_files = os.listdir(os.path.join(PLUGINDIR, i))
		plugin_files = filter(lambda filename: filename.endswith(ftype), plugin_files)
		for j in plugin_files:
			plugin.append(try_load_file(i, j))

	plugin = list(filter(lambda x: x, plugin))

	if args.loud:
		if plugin:
			printer.color_print("Finished loading {type} plugins.", type=ftype)
		else:
			printer.color_print("No {type} plugins found.", type=ftype)
	return plugin

def getPluginNames(ftype):
	if args.no_plugins:
		return []
	plugins = os.listdir(PLUGINDIR)
	plugin_folders = filter(lambda filename: os.path.isdir(os.path.join(PLUGINDIR, filename)), plugins)
	plugins = filter(has_filetype_factory(ftype), plugin_folders)

	plugin = []

	for i in plugins:
		plugin_files = os.listdir(os.path.join(PLUGINDIR, i))
		plugin_files = filter(lambda filename: filename.endswith(ftype), plugin_files)
		for j in plugin_files:
			plugin.append(os.path.abspath(os.path.join(selfpath, os.path.pardir, 'plugins', i, j)))
	return plugin
