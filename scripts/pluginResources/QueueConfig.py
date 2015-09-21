import sys, os
sys.path.append(
	os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from util import *

class PluginPrinterInstance:
	def __init__(self, colorobj=None):
		if not colorobj:
			colorobj = color_config()
		self.colorconfig = colorobj
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