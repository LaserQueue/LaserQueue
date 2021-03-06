import laserqueue
from util import *
color_printing_config.color = ansi_colors.BLUE
color_printing_config.name = "Backend"
config = Config(CONFIGDIR)
import jsonhandler as comm
import sidhandler as sids
import plugins

import websockets
import threading

from parseargv import args

selfpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(selfpath)


class Sockets:
	"""
	A wrapper for a list of websocket objects.
	"""
	def __init__(self):
		self.sockets = []
	def __iter__(self):
		return iter(self.sockets)
	def append(self, obj):
		self.sockets.append(obj)
	def remove(self, obj): 
		key = get_sec_key(obj)
		get = self.get(key)
		if get: self.sockets.remove(get)
	def get(self, key):
		for i in self.sockets:
			if get_sec_key(i) == key:
				return i
	def __getitem__(self, key):
		return self.get(key)

# Initialize required objects
socks = Sockets()
sessions = sids.SIDCache()
queue = laserqueue.Queue()
authed = sessions.allauth()
queuehash = hash(str(queue.queue))

@asyncio.coroutine
def server(websocket, path):
	"""
	The process that's spawned for each websocket connection.
	"""
	global queue, socks, sessions
	# Allow all processes to serve to this
	socks.append(websocket)
	# Serve the latest queue to this socket
	serve_connection(comm.generateData(queue.serialize()), websocket)
	while True:
		# Get the latest message
		message = yield from websocket.recv()
		# Kill off the connection if the socket is broken
		if not message: break
		try:
			# Load the message
			messagedata = json.loads(message)
			# Only use messages if they have an action
			if "action" in messagedata:
				# Make a form of the message used only for display
				displaymessage = message[:]
				if "pass" in messagedata:
					displaymessage = json.loads(displaymessage)
					# Replace the password with asterisks
					displaymessage["pass"] = "*"*len(displaymessage["pass"])
					displaymessage = json.dumps(displaymessage, sort_keys=True)
				authstate = sessions.check(get_sec_key(websocket))
				color = ansi_colors.MAGENTA if authstate and args.loud else ""
				color_print(displaymessage, color=color)
				# Run the processing subroutine
				process(messagedata, websocket)
		except Exception as e: # Error reporting
			color_print(format_traceback(e, "Error while serving WebSockets:"), color=ansi_colors.YELLOW)
			if config["send_notifications"]:
				serve_connection({ # Tell the socket about it
						"action": "notification",
						"title": type(e).__name__,
						"text": str(e)
					}, websocket)
	# Make sure processes don't serve to a dead socket
	socks.remove(websocket)

def process(data, ws):
	"""
	Process data from an incoming socket, and serve the result to everyone.
	"""
	global queue, sessions, socks, queuehash
	if data:
		# Parse the data through the socket command handler
		x = comm.parseData(queue, ws, socks, sessions, data)
		# Back up the queue
		if args.backup:
			json.dump(queue.queue, open("cache.json", "w"), indent=2, sort_keys=True)
		# If the socket handler had an error, report it to the socket
		if x and type(x) is str:
			serve_connection({
					"action": "notification",
					"title": "Failed to process data",
					"text": x
				}, ws)
			color_print(x, color=ansi_colors.YELLOW)
		# If the queue changed, serve it
		if queuehash != hash(str(queue.queue)):
			queuehash = hash(str(queue.queue))
			serve_connections(comm.generateData(queue.serialize()), socks)

def upkeep():
	"""
	Thread to perform tasks asynchronously.
	"""
	global socks, queue, authed, sessions, queuehash, pluginUpkeeps
	while True:
		try:
			# Keep everything in line
			sessions.update()
			# Deauth everyone who dropped from auth
			newauths = sessions.allauth()
			if authed != newauths:
				deauthed = [i for i in authed if i not in newauths]
				authed = sessions.allauth()
				for i in deauthed:
					ws = socks[i]
					if ws:
						serve_connection({"action":"deauthed"}, ws)
			# Remove closed socks
			for i in socks:
				if not i.open:
					sessions.sids.remove(sessions._get(get_sec_key(i)))

			for module in pluginUpkeeps:
				try:
					module.upkeep(queue=queue, sessions=sessions, sockets=socks)
				except:
					color_print(format_traceback(e, format("Error while processing {plugin}.upkeep:", plugin=module.__name__)), color=ansi_colors.YELLOW)
					pluginUpkeeps.remove(module)

			# If the queue changed, serve it
			queue.metapriority()
			if queuehash != hash(str(queue.queue)):
				queuehash = hash(str(queue.queue))
				serve_connections(comm.generateData(queue.serialize()), socks)

			time.sleep(config["refreshRate"]/1000)
		except Exception as e: # Error reporting
			color_print(format_traceback(e, "Error in upkeep thread:"), color=ansi_colors.YELLOW)

def main():
	"""
	Setup and run all subroutines.
	"""
	global socks, queue, authed, sessions, queuehash, upkeepThread, pluginUpkeeps

	pluginList = plugins.getPlugins()
	pluginUpkeeps = list(filter(lambda module: hasattr(module, "upkeep"), pluginList))
	comm.buildCommands(pluginList)
	laserqueue.buildLists(pluginList)

	# Load the queue if -b is used
	if args.backup:
		if os.path.exists("cache.json"):
			queue = laserqueue.Queue.load(open("cache.json"))
		else:
			json.dump({}, open("cache.json", "w"))

	color_print("Serving WebSockets on 0.0.0.0 port {port} ...", port=config["port"])

	# Create the upkeep thread
	upkeepThread = threading.Thread(target=upkeep)
	upkeepThread.daemon = True
	upkeepThread.start()

	# Create the server event loop
	start_server = websockets.serve(server, "0.0.0.0", config['port'])
	loop = asyncio.get_event_loop()
	try:
		loop.run_until_complete(start_server)
		loop.run_forever()
	except KeyboardInterrupt:
		quit(0)




if __name__ == "__main__":
	main()