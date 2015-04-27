#!/usr/bin/env python

import asyncio
import websockets
import json
import os
import time

@asyncio.coroutine
def hello(websocket, path):
	while True:
		message = yield from websocket.recv()
		temppath = os.path.expanduser(os.path.join("~", "AppData", "Local", "Temp"))
		try:
			messagedata = json.loads(message)
			if message != None and ("action" in messagedata and messagedata["action"] != "null"): print(message)
			if os.path.exists(os.path.join(temppath, "topage.json")):
				if messagedata:
					if message != None and ("action" in messagedata and messagedata["action"] != "null"):
						print("saving message")
					messagef = open(os.path.join(temppath, "toscript.json"), "w")
					json.dump(messagedata, messagef)
					messagef.close()

					time.sleep(0.5)

					dataf = open(os.path.join(temppath, "topage.json"))
					data = json.load(dataf)
					dataf.close()
					yield from websocket.send(json.dumps(data))
		except:
			pass
			
		

start_server = websockets.serve(hello, 'yrsegal.local', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()