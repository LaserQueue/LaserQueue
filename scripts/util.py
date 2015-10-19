from wireutils import *
import ssl, urllib.request, io, uuid

DEFAULTCONFIGDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "www", "defaultconf.json"))
CONFIGDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "www", "config.json"))

# Functions for serving to sockets
import asyncio

def get_sec_key(ws):
	"""
	Get the Sec key of the websocket `ws`, used to identify it.
	"""
	return dict(ws.raw_request_headers)['Sec-WebSocket-Key']

def serve_connections_generator(jdata, socks):
	"""
	A generator function used to serve to every socket in `socks`.
	"""
	for i in socks:
		if i.open:
			yield from i.send(json.dumps(jdata, sort_keys=True))

def serve_connection_generator(jdata, ws):
	"""
	A generator function used to serve to the `ws` socket.
	"""
	if ws.open:
		yield from ws.send(json.dumps(jdata, sort_keys=True))
		
serve_connections = lambda jdata, socks: list(serve_connections_generator(jdata, socks))
serve_connection = lambda jdata, ws: list(serve_connection_generator(jdata, ws))

if not hasattr(ssl, '_create_default_https_context'): # Some operating systems don't have the default https context.
	if hasattr(ssl, '_create_unverified_context'):
		ssl._create_default_https_context = ssl._create_unverified_context
	elif hasattr(ssl, 'create_default_context'):
		ssl._create_default_https_context = ssl.create_default_context
	else:
		conf = json.load(open(DEFAULTCONFIGDIR))
		def fakeopen(*args, **kwargs):
			color_print("""Cannot access the internet via https.
			          This is due to a python bug with some operating systems.
			          Because of this, updates will not be performed.
			          To see if you need to update, go to 
			          {blue}{line}{target}{endc}{color}.
			          (Current version: {endc}{version}{color})""", color=ansi_colors.RED, strip=True, 
			          version = conf["version"], target=conf["update_repo"])
			return io.BytesIO(bytes("{}", 'utf8'))
		urllib.request.urlopen = fakeopen


