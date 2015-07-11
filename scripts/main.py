import laserqueue
from config import *
cprintconf.color = bcolors.BLUE
cprintconf.name = "Backend"
config = Config(os.path.join("..","www","config.json"))
import jsonhandler as comm
import sidhandler as sids

import json
import os, time
import asyncio, websockets
import threading

from parseargv import args

selfpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(selfpath)


class Sockets:
	def __init__(self):
		self.sockets = []
	def __iter__(self):
		return iter(self.sockets)
	def append(self, obj):
		self.sockets.append(obj)
	def remove(self, obj): 
		key = getsec(obj)
		get = self.get(key)
		if get: self.sockets.remove(get)
	def get(self, key):
		for i in self.sockets:
			if getsec(i) == key:
				return i
	def __getitem__(self, key):
		return self.get(key)

socks = Sockets()

sessions = sids.SIDCache()
queue = laserqueue.Queue()
authed = sessions.allauth()
queuehash = hash(str(queue.queue))

@asyncio.coroutine
def server(websocket, path):
	global queue, socks
	socks.append(websocket)
	serveToConnection(comm.generateData(queue.serialize()), websocket)
	while True:
		message = yield from websocket.recv()
		if not message: break
		try:
			messagedata = json.loads(message)
			if "action" in messagedata:
				displaymessage = message[:]
				if "pass" in messagedata:
					displaymessage = json.loads(displaymessage)
					displaymessage["pass"] = "*"*len(displaymessage["pass"])
					displaymessage = json.dumps(displaymessage, sort_keys=True)
				cprint(displaymessage)

				process(messagedata, websocket)
		except Exception as e: 
			cprint(bcolors.YELLOW + "{}: {}".format(type(e).__name__, str(e)))
			if config["send_notifications"]:
				serveToConnection({
						"action": "notification",
						"title": type(e).__name__,
						"text": str(e)
					}, websocket)
	socks.remove(websocket)

def process(data, ws):
	global queue, sessions, socks, queuehash
	if data:
		x = comm.parseData(queue, ws, socks, sessions, data)
		if args.backup:
			json.dump(queue.queue, open("cache.json", "w"), indent=2, sort_keys=True)
		if x and type(x) is str:
			serveToConnection(json.dumps({
					"action": "notification",
					"title": "Failed to process data",
					"text": x
				}, sort_keys = True), ws)
			cprint(bcolors.YELLOW + x)
		if queuehash != hash(str(queue.queue)):
			queuehash = hash(str(queue.queue))
			serveToConnections(comm.generateData(queue.serialize()), socks)

def upkeep():
	global queue, authed, sessions
	while True:
		try:
			sessions.update()
			newauths = sessions.allauth()
			if authed != newauths:
				deauthed = [i for i in authed if i not in newauths]
				authed = sessions.allauth()
				for i in deauthed:
					ws = socks[i]
					serveToConnection({"action":"deauthed"}, ws)
			for i in socks:
				if not i.open:
					sessions.sids.remove(sessions._get(getsec(i)))
			time.sleep(config["refreshRate"]/1000)
		except Exception as e:
			cprint(bcolors.YELLOW + "{}: {}".format(type(e).__name__, str(e)))

def main():
	global queue, authed, sessions, queuehash, upkeepThread
	if args.backup:
		if os.path.exists("cache.json"):
			queue = laserqueue.Queue.load(open("cache.json"))
		else:
			json.dump({}, open("cache.json", "w"))
	cprint("Serving WebSockets on 0.0.0.0 port "+config["port"]+" ...")

	upkeepThread = threading.Thread(target=upkeep)
	upkeepThread.daemon = True
	upkeepThread.start()

	start_server = websockets.serve(server, "0.0.0.0", config['port'])
	loop = asyncio.get_event_loop()
	try:
		loop.run_until_complete(start_server)
		loop.run_forever()
	except KeyboardInterrupt:
		quit(0)




if __name__ == "__main__":
	main()