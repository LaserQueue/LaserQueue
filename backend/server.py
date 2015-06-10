#!/usr/bin/env python

import asyncio
import websockets
import json
import os
import time
import tempfile

from parseargv import args

from configloader import config

temppath = tempfile.gettempdir()

selfpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(selfpath)

@asyncio.coroutine
def hello(websocket, path):
	stamp = time.time()
	while stamp-time.time()<config["serverRefreshRate"]/1000:
		if not websocket.open:
			break
		message = yield from websocket.recv()
		try:
			messagedata = json.loads(message)
			if message != None and ("action" in messagedata and messagedata["action"] not in ["null", "auth", "uuddlrlrba"]): print(message)
			if os.path.exists(os.path.join(temppath, "topage.json")): 
				if messagedata:
					if message != None and "action" in messagedata:
						if messagedata["action"] not in ["null", "auth", "uuddlrlrba"]:
							print("saving message")
						messagef = open(os.path.join(temppath, "toscript.json"), "w")
						json.dump(messagedata, messagef)
						messagef.close()

						time.sleep(0.05)

						dataf = open(os.path.join(temppath, "topage.json"))
						data = json.load(dataf)
						dataf.close()
						yield from websocket.send(json.dumps(data))
		except:
			pass
			
		
def main():
	print("Serving WebSockets on "+config['host']+" port "+config["port"]+" ...")
	start_server = websockets.serve(hello, config['host'], config['port'])

	asyncio.get_event_loop().run_until_complete(start_server)
	asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
	main()