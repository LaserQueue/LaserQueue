import os, json, time

class Config:
	def __init__(self, path):
		self.path = path
		self.lastmodtime = os.path.getctime(path)
		self.data = json.load(open(path))
	def __getitem__(self, y):
		if os.path.getctime(self.path) > self.lastmodtime:
			self.data = json.load(open(self.path))
			lastmodtime = os.path.getctime(self.path)
		return self.data[y]

class WalkingConfig(Config):
	def __init__(self, path):
		filename = os.path.basename(path)
		findpath = os.path.dirname(path)
		self.path = None
		while True:
			if filename in os.listdir(findpath):
				self.path = os.path.join(findpath, filename)
				break
			elif os.path.abspath(findpath) == os.path.sep:
				raise FileNotFoundError(filename+" not found in directory tree.")
			findpath = os.path.join(findpath, "..")
		self.lastmodtime = os.path.getctime(self.path)
		self.data = json.load(open(self.path))

def date_time_string(timestamp=None):
	"""Return the current date and time formatted for a message header."""
	monthname = [None,
							 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
							 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	now = time.time()
	year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
	hh = "0" + str(hh) if hh < 10 else str(hh)
	mm = "0" + str(mm) if mm < 10 else str(mm)
	ss = "0" + str(ss) if ss < 10 else str(ss)
	day = "0" + str(day) if day < 10 else str(day)
	
	s = (bcolors.MAGENTA + "[{0}/{1}/{2} {3}:{4}:{5}] " + bcolors.ENDC).format(
		day, monthname[month], year, hh, mm, ss)
	return s

class bcolors:
	BLACK = '\033[30m'
	DARKRED = '\033[31m'
	DARKGREEN = '\033[32m'
	DARKYELLOW = '\033[33m'
	DARKBLUE = '\033[34m'
	PURPLE = '\033[35m'
	DARKCYAN = '\033[36m'
	GRAY = '\033[37m'
	DARKGRAY = '\033[90m'
	RED = '\033[91m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	BLUE = '\033[94m'
	MAGENTA = '\033[95m'
	CYAN = '\033[96m'
	WHITE = '\033[97m'
	ENDC = '\033[0m'

class colorconf:
	def __init__(self):
		self.color = bcolors.WHITE
		self.name = "Generic"

cprintconf = colorconf()


lastprinted = None

def cprint(text):
	global lastprinted
	if text == lastprinted: return
	lastprinted = text
	prints = text.split("\n")
	originstr = cprintconf.color + "[" + cprintconf.name + "] " + bcolors.ENDC
	print(date_time_string() + originstr + prints[0] + bcolors.ENDC)
	for i in prints[1:]:
		print(" "*(26+len(cprintconf.name)) + i + bcolors.ENDC)

def cinput(text):
	prints = text.split("\n")
	originstr = cprintconf.color + "[" + cprintconf.name + "] " + bcolors.ENDC
	if len(prints) > 1: 
		print(date_time_string() + originstr + prints[0])
		for i in prints[1:-1]:
			print(" "*(26+len(cprintconf.name)) + i)
		return input(" "*(26+len(cprintconf.name)) + prints[-1] + bcolors.ENDC)
	else:
		return input(date_time_string() + originstr + prints[0] + bcolors.ENDC)