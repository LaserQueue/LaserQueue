import sys, os
sys.path.append(
	os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from util import *

class PluginPrinterInstance:
	def __init__(self, *args):
		if not args:
			colorobj = color_config()
		elif len(args) == 1:
			if isinstance(args[0], color_config):
				colorobj = args[0]
			elif isinstance(args[0], str):
				colorobj = color_config()
				colorobj.name = args[0]
			else:
				raise TypeError(format("Expected type `color_config`, got type `{type}`", type=type(args[0]).__name__))
		elif len(args) == 2:
			colorobj = color_config()
			colorobj.color = args[0]
			colorobj.name = args[1]
		else:
			raise TypeError(format("PluginPrinterInstance() takes at most 2 positional arguments, but {num} were given", type=len(args)))
		self.colorconfig = colorobj
	def set(self, color, name):
		self.colorconfig.color = color
		self.colorconfig.name = name
	def setname(self, string):
		self.colorconfig.name = string
	def setcolor(self, string):
		self.colorconfig.color = string
	def color_print(self, *args, **kwargs):
		kwargs["colorconfig"] = self.colorconfig
		color_print(*args, **kwargs)
	def color_input(self, *args, **kwargs):
		kwargs["colorconfig"] = self.colorconfig
		color_input(*args, **kwargs)

CONFIGDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 
	os.path.pardir, os.path.pardir, "www", "config.json"))