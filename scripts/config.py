import os, json, time

def _fillblanks(odict, adict):
	return dict(adict, **odict)

class Config:
	def __init__(self, path):
		self.path = path
		self.lastmodtime = os.path.getctime(path)
		self.data = json.load(open(path))
	def reload(self):
		if os.path.getctime(self.path) > self.lastmodtime:
			self.data = json.load(open(self.path))
			lastmodtime = os.path.getctime(self.path)
	def __getitem__(self, y):
		self.reload()
		return self.data[y]
	def __contains__(self, key):
		self.reload()
		return key in self.data
	def get(self, k, d=None):
		self.reload()
		return self.data.get(k, d)

class WalkingConfig(Config):
	def __init__(self, path, refpath, userrefpath):
		self.walkload(path, refpath, userrefpath)
	def modtimes(self):
		return [os.path.getctime(i) for i in self.files]
	def walkload(self, path, refpath, userrefpath):
		reffile = self.getfilename(refpath)
		refconf = json.load(open(reffile))
		usrfile = self.getfilename(userrefpath, False)
		if usrfile:
			usrconf = json.load(open(usrfile))
			refconf = _fillblanks(usrconf, refconf)
		filename = os.path.basename(path)
		findpath = os.path.dirname(path)
		items = {}
		files = []
		while os.path.abspath(findpath) != os.path.sep:
			if filename in os.listdir(findpath):
				configfile = json.load(open(os.path.join(findpath, filename)))
				files.append(os.path.join(findpath, filename))
				items = _fillblanks(items, configfile)
			findpath = os.path.join(findpath, "..")
		items = _fillblanks(items, refconf)
		self.data = items
		self.refconf = refconf
		self.files = files
		self.lastmods = self.modtimes()
	def reload(self):
		items = {}
		if self.modtimes() != self.lastmods:
			lastmods = self.modtimes()
			for i in self.files:
				configfile = json.load(open(i))
				items = _fillblanks(items, configfile)
			self.data = _fillblanks(items, self.refconf)
	def getfilename(self, path, strict=True):
		filename = os.path.basename(path)
		findpath = os.path.dirname(path)
		reffile = None
		while True:
			if filename in os.listdir(findpath):
				reffile = os.path.join(findpath, filename)
				break
			elif os.path.abspath(findpath) == os.path.sep:
				if strict:
					raise FileNotFoundError(filename+" not found in directory tree.")
				else:
					break
			findpath = os.path.join(findpath, "..")
		return reffile







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