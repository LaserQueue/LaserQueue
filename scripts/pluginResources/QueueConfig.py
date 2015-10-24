import sys, os
sys.path.append(
	os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from util import *

CONFIGDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 
	os.path.pardir, os.path.pardir, "www", "config.json"))