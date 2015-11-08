from wireutils import *
from parseargv import args as argvs
import ssl, urllib.request, io, uuid, random

Registry.register = Registry.on

if color_supported: 
	ansi_colors.RANDOM = "\033[3%dm" % random.randint(1,8)
	ansi_colors.MAKERANDOM = lambda significant=3: "\033[%s%dm" % str(significant), random.randint(1,8)
else:
	ansi_colors.RANDOM = ''
	ansi_colors.MAKERANDOM = lambda _=None: ''
ansi_colors.COLORS["random"] = ansi_colors.RANDOM

DEFAULTCONFIGDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "www", "defaultconf.json"))
CONFIGDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "www", "config.json"))

class MergerConfig(Config):
	def __init__(self, path, defpath=""):
		if not defpath:
			self = Config(path)
		else:
			self.path = path
			self.defpath = path
			defdata = json.load(open(defpath))
			try:
				data = json.load(open(path))
				self.new = False
			except:
				data = {}
				self.new = True
			self.data = dict(defdata, **data)
			out = json.dumps(self.data, sort_keys=True, indent=2)
			write_file(path, out)
			self.lastmodtime = os.path.getctime(path) # get the last modified time of the target file

class Printer:
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
			raise TypeError(format("Printer() takes at most 2 positional arguments, but {num} were given", type=len(args)))
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
		if not argvs.shh: color_print(*args, **kwargs)
	def color_input(self, *args, **kwargs):
		kwargs["colorconfig"] = self.colorconfig
		if not argvs.shh: color_input(*args, **kwargs)

# Functions for serving to sockets
def get_sec_key(ws):
	"""
	Get the Sec key of the websocket `ws`, used to identify it.
	"""
	return dict(ws.raw_request_headers)['Sec-WebSocket-Key']

def serve_connections_generator(jdata, socks):
	"""
	A generator function used to serve to every socket in `socks`.
	"""
	for ws in socks:
		if ws.open:
			yield from ws.send(json.dumps(jdata, sort_keys=True))

def serve_connection_generator(jdata, ws):
	"""
	A generator function used to serve to the `ws` socket.
	"""
	if ws.open:
		yield from ws.send(json.dumps(jdata, sort_keys=True))
		
serve_connections = lambda jdata, socks: list(serve_connections_generator(jdata, socks))
serve_connection = lambda jdata, ws: list(serve_connection_generator(jdata, ws))

def write_file(path, data, printer=None):
	"""
	Write to a file, being careful to respect sudo.
	"""
	exists = os.path.exists(path)
		
	with open(path, "w") as fs:
		fs.write(data)

	if not exists and os.name != "nt" and not os.geteuid():
		try:
			uid = os.environ.get('SUDO_UID')
			gid = os.environ.get('SUDO_GID')
			if uid:
				os.chown(path, int(uid), int(gid))
		except:
			if printer:
				printer.color_print(format("WARNING: {file} created as root.", file=os.path.basename(path)), color=ansi_colors.YELLOW)

if not hasattr(ssl, '_create_default_https_context'): # Some operating systems don't have the default https context.
	if hasattr(ssl, '_create_unverified_context'):
		ssl._create_default_https_context = ssl._create_unverified_context
	elif hasattr(ssl, 'create_default_context'):
		ssl._create_default_https_context = ssl.create_default_context
	else:
		config = json.load(open(DEFAULTCONFIGDIR))
		urlprinter = Printer(ansi_colors.DARKRED, "URL Error")
		def fakeopen(*args, **kwargs):
			urlprinter.color_print("""Cannot access the internet via https.
			                       This is due to a python bug with some operating systems.
			                       Because of this, updates will not be performed.
			                       To see if you need to update, go to
			                       {blue}{line}{target}{endc}{color}.
			                       (Current version: {endc}{version}{color})""", color=ansi_colors.RED, strip=True,
			                       version = config["version"], target=config["updateRepo"])
			return io.BytesIO(bytes("{}", 'utf8'))
		urllib.request.urlopen = fakeopen
