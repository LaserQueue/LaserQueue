import os, json, time

import traceback
def tbformat(e, text="Traceback (most recent call last):"):
	"""
	Format a traceback into a printable string.
	"""
	trace = traceback.extract_tb(e.__traceback__) # Get the traceback object
	error = "{}\n".format(text) # Start out with `text`

	# Iterate through the traceback and add each iteration to the string
	for filename,lineno,function,message in trace:
		error += "  File \"{}\", line {}, in {}\n".format(filename, lineno, function)
		if message: 
			error += "    {}\n".format(message)

	# Add the type and message of the error
	error += str(type(e).__name__)
	if str(e): error += ": {}".format(str(e))

	return error 

class Config:
	"""
	A JSON read-only loader that will update automatically from `path`.
	"""
	def __init__(self, path):
		self.path = path
		self.lastmodtime = os.path.getctime(path) # get the last modified time of the target file
		self.data = json.load(open(path))
	def reload(self):
		if os.path.getctime(self.path) > self.lastmodtime: # check the last modified time of the target file
			self.data = json.load(open(self.path))
			self.lastmodtime = os.path.getctime(self.path)

	# These are extensions of self.data's methods, except they run self.reload.
	def __getitem__(self, y):
		self.reload()
		return self.data[y]
	def __contains__(self, key):
		self.reload()
		return key in self.data
	def get(self, k, d=None):
		self.reload()
		return self.data.get(k, d)


# Functions for serving to sockets
import asyncio

def getsec(ws):
	"""
	Get the Sec key of the websocket `ws`, used to identify it.
	"""
	return dict(ws.raw_request_headers)['Sec-WebSocket-Key']

def serveGen(jdata, socks):
	"""
	A generator function used to serve to every socket in `socks`.
	"""
	for i in socks:
		if i.open:
			yield from i.send(json.dumps(jdata, sort_keys=True))

def serveToConnections(jdata, socks):
	"""
	A function which extracts every iteration of the generator `serveGen`.
	"""
	list(serveGen(jdata, socks))

def serveTo(jdata, ws):
	"""
	A generator function used to serve to the `ws` socket.
	"""
	if ws.open:
		yield from ws.send(json.dumps(jdata, sort_keys=True))

def serveToConnection(jdata, ws):
	"""
	A function which extracts every iteration of the generator `serveTo`.
	"""
	list(serveTo(jdata, ws))




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

cprintconf = colorconf() # create the instance of colorconf used to configure cprint and cinput

lastprinted = None

def cprint(text, color="", strip=False, func=print, add_newline=False):
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

def cinput(text, color="", strip=False, func=input, add_newline=False):
	"""
	Pretty print `text`, with `color` as its color. Take input using `func` on the last line.
	If `strip`, then remove whitespace from both sides of each line.
	"""
	text = str(text)
	# Split the text by lines
	if strip:
		prints = [i.strip().rstrip() for i in text.split("\n")]
		prints[-1] += " " # Add a spacing to the last line
	else:
		prints = text.split("\n")

	originstr = cprintconf.tag()
	# Print in order if there's more than one line
	if len(prints) > 1: 
		print("{}{}{}{}".format(date_time_string(), originstr, 
		                        color, prints[0]))
		if add_newline: func("\n")

		for i in prints[1:-1]:
			print("{}{}{}".format(cprintconf.whitespace(), 
			                      color, i))
			if add_newline: func("\n")

		return func("{}{}{}{}".format(cprintconf.whitespace(), color,
		                              prints[-1], bcolors.ENDC))
		if add_newline: func("\n")
	else:
		return func("{}{}{}{}{}".format(date_time_string(), originstr, color,
		                                prints[0], bcolors.ENDC))
		if add_newline: func("\n")

