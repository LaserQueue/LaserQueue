from laserqueue import Queue
from configloader import config
import jsonhandler as comm
import sidhandler as sids
import tempfile

import json
import os.path
import time

from parseargv import args

temppath = tempfile.gettempdir()

selfpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(selfpath)

def main():
	shamed = []
	queue = Queue()

	json.dump({}, open(os.path.join(temppath, "toscript.json"), "w"))

	if args.backup:
		if os.path.exists("cache.json"):
			queue = Queue.load(open("cache.json"))
		else:
			json.dump({}, open("cache.json", "w"))
		sessions = sids.loadcache()
	else:
		sessions = sids.SIDCache()

	stamp = time.time()
	while True:
		if os.path.exists(os.path.join(temppath, "toscript.json")):
			dataf = open(os.path.join(temppath, "toscript.json"))
			datat = dataf.read()
			if datat and datat != "{}":
				try:
					data = json.loads(datat)
					queue.metapriority()
					x = comm.parseData(queue, sessions, data, shamed)
					if "action" in data and data["action"] != "null":
						print(json.dumps(data, indent=2))
						sessions.update()
						if args.backup:
							json.dump(queue.queue, open("cache.json", "w"), indent=2)

							sids.cache(sessions)
					if x and type(x) is str:
						if x == "uuddlrlrba" and config["easter_eggs"]:
							json.dump({"action":"rickroll"}, open(os.path.join(temppath, "topage.json"), "w"))
							time.sleep((config["refreshRate"]*1.5)/1000)
						elif x == "refresh" and config["allow_force_refresh"]:
							json.dump({"action":"refresh"}, open(os.path.join(temppath, "topage.json"), "w"))
							time.sleep((config["refreshRate"]*1.5)/1000)
						elif x == "sorry":
							if data["sid"][:int(len(data["sid"])/2)] in shamed:
								shamed.remove(data["sid"][:int(len(data["sid"])/2)])
						else:
							print(x)
						time.sleep(0.2)
					else:
						if x is False:
							shamed.append(data["sid"][:int(len(data["sid"])/2)])
						json.dump(comm.generateData(queue, sessions, shamed), open(os.path.join(temppath, "topage.json"), "w"))
						json.dump({}, open(os.path.join(temppath, "toscript.json"), "w"), {})
						if data["action"] != "null": print(queue.queue)
				except Exception as e: 
					print(e)
				
		time.sleep(0.01)



if __name__ == "__main__":
	main()