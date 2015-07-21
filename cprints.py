# Only imported if Python is outdated, so no errors are raised when python runs into the asyncio code.

import time

def date_time_string(timestamp=None):
	"""
	Return the current date and time formatted for a message header.
	"""
	monthname = [None,
							 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
							 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

	now = time.time()
	year, month, day, hh, mm, ss, x, y, z = time.localtime(now)

	# Add zeroes to keep the length of the timestamp constant
	hh = "0{}".format(hh) if hh < 10 else str(hh)
	mm = "0{}".format(mm) if mm < 10 else str(mm)
	ss = "0{}".format(ss) if ss < 10 else str(ss)
	day = "0{}".format(day) if day < 10 else str(day)
	
	s = (bcolors.MAGENTA + "[{0}/{1}/{2} {3}:{4}:{5}] " + bcolors.ENDC).format(
		day, monthname[month], year, hh, mm, ss)
	return s



class bcolors: # All color codes
	"""
	A helper class containing colors (for pretty printing.)
	"""
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
	"""
	An object used to configure cprint and cinput.
	"""
	def __init__(self):
		self.color = bcolors.WHITE
		self.name = "Generic"
	def tag(self):
		"""
		Return the tag for pretty printing from the config.
		"""
		return "{}[{}] {}".format(self.color, self.name, bcolors.ENDC)
	def whitespace(self):
		"""
		Return the whitespace for non-printed lines.
		"""
		return " "*(26+len(self.name))

cprintconf = colorconf() # create the instance of colorconf used to configure cprint

lastprinted = None

# A wrapper for print that accepts both versions.
def printf(string):
	print(string)

def cprint(text, color="", strip=False, func=printf, add_newline=False):
	"""
	Pretty print `text`, with `color` as its color, using `func`.
	If `strip`, then remove whitespace from both sides of each line.
	"""
	global lastprinted
	text = str(text)

	# Make sure not to print the same thing twice
	if text == lastprinted: return
	lastprinted = text

	# Split the text by lines
	if strip:
		prints = [i.strip().rstrip() for i in text.split("\n")]
	else:
		prints = text.split("\n")


	originstr = cprintconf.tag()
	func("{}{}{}{}{}".format(date_time_string(), originstr, 
	                        color, prints[0], bcolors.ENDC)) # Print the first line with a timestamp
	if add_newline: func("\n")

	for i in prints[1:]:
			func("{}{}{}{}".format(cprintconf.whitespace(), 
			                      color, i, bcolors.ENDC)) # Print all consecutive lines
			if add_newline: func("\n")
