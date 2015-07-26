import sys, os
sys.path.append(
	os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from config import *

class PluginPrinterInstance:
	def __init__(self, colorobj=None):
		if not colorobj:
			colorobj = colorconf()
		self.colorconfig = colorobj
	def setname(self, string):
		self.colorconfig.name = string
	def setcolor(self, string):
		self.colorconfig.color = string
	def cprint(self, *args, **kwargs):
		kwargs["colorconfig"] = self.colorconfig
		cprint(*args, **kwargs)
	def cinput(self, *args, **kwargs):
		kwargs["colorconfig"] = self.colorconfig
		cinput(*args, **kwargs)

CONFIGDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 
	os.path.pardir, os.path.pardir, "www", "config.json"))