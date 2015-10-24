import laserqueue
from util import *
printer = Printer(ansi_colors.BLUE, "Backend")
config = Config(CONFIGDIR)
import jsonhandler as comm
import sidhandler as sids
import plugins

import asyncio
import websockets
import threading

from parseargv import args

selfpath = os.path.dirname(os.path.realpath(__file__))


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
				displaymessage = json.loads(message)
				if "pass" in messagedata:
					# Replace the password with asterisks
					displaymessage["pass"] = "*"*len(displaymessage["pass"])
				for key in messagedata:
					if isinstance(messagedata[key], str):
						displaymessage[key] = displaymessage[key].replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")
						if len(messagedata[key]) > 64:
							displaymessage[key] = displaymessage[key][:61] + "{bold}{darkgray}...{endc}"

				authstate = sessions.check(get_sec_key(websocket))
				color = ansi_colors.MAGENTA if authstate and args.loud else ""
				printer.color_print(json.dumps(displaymessage, sort_keys=True), color=color)
				# Run the processing subroutine
				process(messagedata, websocket)
		except Exception as e: # Error reporting
			printer.color_print(format_traceback(e, "Error while serving WebSockets:"), color=ansi_colors.YELLOW)
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
		x = comm.parseData(queue, ws, socks, sessions, data, printer)
		# Back up the queue
		if args.backup:
			out = json.dumps(queue.queue, indent=2, sort_keys=True)
			writeFile("cache.json", out, printer)
		# If the socket handler had an error, report it to the socket
		if x and type(x) is str:
			serve_connection({
					"action": "notification",
					"title": "Failed to process data",
					"text": x
				}, ws)
			printer.color_print(x, color=ansi_colors.YELLOW)
		# If the queue changed, serve it
		if queuehash != hash(str(queue.queue)):
			queuehash = hash(str(queue.queue))
			serve_connections(comm.generateData(queue.serialize()), socks)

def upkeep():
	"""
	Thread to perform tasks asynchronously.
	"""
	global socks, queue, sessions, upkeeps
	while True:
		try:
			upkeepsDupe = upkeeps[:]
			for upkeepf in upkeepsDupe:
				try:
					regdupe = Registry()
					regdupe.events = dict(reg.events)
					upkeepf(queue=queue, sessions=sessions, sockets=socks, registry=regdupe)
				except Exception as e:
					printer.color_print(format_traceback(e, "Error while processing upkeep:"), color=ansi_colors.YELLOW)
					upkeeps.remove(upkeepf)

			time.sleep(config["refreshRate"]/1000)
		except Exception as e: # Error reporting
			printer.color_print(format_traceback(e, "Error in upkeep thread:"), color=ansi_colors.YELLOW)

def watchSessions(**kwargs):
	global authed
	# Keep everything in line
	kwargs["sessions"].update()
	# Deauth everyone who dropped from auth
	newauths = kwargs["sessions"].allauth()
	if authed != newauths:
		deauthed = [i for i in authed if i not in newauths]
		authed = kwargs["sessions"].allauth()
		for i in deauthed:
			ws = kwargs["sockets"][i]
			if ws:
				serve_connection({"action":"deauthed"}, ws)
	# Remove closed socks
	for i in kwargs["sockets"]:
		if not i.open:
			kwargs["sessions"].sids.remove(sessions._get(get_sec_key(i)))

def watchQueue(**kwargs):
	global queuehash
	# If the queue changed, serve it
	kwargs["queue"].metapriority()
	if queuehash != hash(str(kwargs["queue"].queue)):
		queuehash = hash(str(kwargs["queue"].queue))
		serve_connections(comm.generateData(kwargs["queue"].serialize()), kwargs["sockets"])

def reloadplugins(filetype, plugin_path):
	pl = plugins.getPluginFiletype(filetype)
	plugins = "\n".join(pl)
	writeFile(plugin_path, plugins, printer)

plugin_js_path = os.path.join(selfpath, os.path.pardir, "www", "dist", "js", "plugins.js")
plugin_css_path = os.path.join(selfpath, os.path.pardir, "www", "dist", "css", "plugins.css")
def watchPlugins(**kwargs):
	jsstep, cssstep = False, False
	pluginJSFilesDupe, pluginCSSFilesDupe = dict(pluginJSFiles), dict(pluginCSSFiles)
	for i in pluginJSFilesDupe:
		try:
			if os.path.getctime(i) > pluginJSFiles[i]:
				pluginJSFiles[i] = os.path.getctime(i)
				if not jsstep:
					toprint = "Reloading JS plugins."
					if args.loud: toprint += "\n({file} updated.)"
					plugins.printer.printer.color_print(toprint, file=os.path.basename(i))
					reloadplugins(".min.js", plugin_js_path)
					jsstep = True
		except:
			del pluginJSFiles[i]
			if not jsstep:
				toprint = "Reloading JS plugins."
				if args.loud: toprint += "\n({file} removed.)"
				plugins.printer.printer.color_print(toprint, file=os.path.basename(i))
				reloadplugins(".min.js", plugin_js_path)
				jsstep = True
				
	for i in pluginCSSFilesDupe:
		try:
			if os.path.getctime(i) > pluginCSSFiles[i]:
				pluginCSSFiles[i] = os.path.getctime(i)
				if not cssstep:
					toprint = "Reloading CSS plugins."
					if args.loud: toprint += "\n({file} updated.)"
					plugins.printer.printer.color_print(toprint, file=os.path.basename(i))
					reloadplugins(".min.css", plugin_css_path)
					cssstep = True
		except:
			del pluginJSFiles[i]
			if not cssstep:
				toprint = "Reloading CSS plugins."
				if args.loud: toprint += "\n({file} removed.)"
				plugins.printer.printer.color_print(toprint, file=os.path.basename(i))
				reloadplugins(".min.css", plugin_css_path)
				cssstep = True

def main():
	"""
	Setup and run all subroutines.
	"""
	global socks, reg, queue, authed, sessions, queuehash, upkeepThread, upkeeps, pluginJSFiles, pluginCSSFiles

	pluginList, reg = plugins.getPlugins()
	pluginJSFiles = {i: os.path.getctime(i) for i in plugins.getPluginNames(".min.js")}
	pluginCSSFiles = {i: os.path.getctime(i) for i in plugins.getPluginNames(".min.css")}
	upkeeps = [watchSessions, watchQueue]
	if pluginJSFiles or pluginCSSFiles:
		upkeeps.append(watchPlugins)
	upkeeplist = reg.events.get('upkeep', {})
	upkeeps = [(i,upkeeplist[i]) for i in upkeeplist]
	for jobid, job in upkeeps:
		if job and hasattr(job[0], "__call__"):
			upkeeps.append(job[0])
	comm.buildCommands(pluginList, reg)
	laserqueue.buildLists(pluginList, reg)

	# Load the queue if -b is used
	if args.backup:
		if os.path.exists("cache.json"):
			queue = laserqueue.Queue.load(open("cache.json"))
		else:
			writeFile("cache.json", "{}", printer)

	printer.color_print("Serving WebSockets on 0.0.0.0 port {port} ...", port=config["port"])

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
