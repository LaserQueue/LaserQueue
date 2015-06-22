from laserqueue import Queue
from config import *
cprintconf.color = bcolors.BLUE
cprintconf.name = "Backend"
config = WalkingConfig(os.path.join("..","www","config.json"), 
	os.path.join("..","www","defaultconf.json"), 
	os.path.join("..","www","userconf.json"))
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
	cprint("Ready to process data ...")
	try:
		while True:
			if os.path.exists(os.path.join(temppath, "toscript.json")):
				dataf = open(os.path.join(temppath, "toscript.json"))
				datat = dataf.read()
				if datat and datat != "{}":
					try:
						data = json.loads(datat)
						queue.metapriority()
						x = comm.parseData(queue, sessions, data)
						if "action" in data and data["action"] != "null":
							sessions.update()
							if args.backup:
								json.dump(queue.queue, open("cache.json", "w"), indent=2)

								sids.cache(sessions)
						if x and type(x) is str:
							if x == "uuddlrlrba":
								if config["easter_eggs"]:
									json.dump({"action":"rickroll"}, open(os.path.join(temppath, "topage.json"), "w"))
									time.sleep((config["refreshRate"]*1.5)/1000)
								else:
									cprint(bcolors.YELLOW + "This is a serious establishment, son. I'm dissapointed in you.")
							elif x == "refresh":
								if config["allow_force_refresh"]:
									json.dump({"action":"refresh"}, open(os.path.join(temppath, "topage.json"), "w"))
									time.sleep((config["refreshRate"]*1.5)/1000)
								else:
									cprint(bcolors.YELLOW + "Force refresh isn't enabled. (config.json, allow_force_refresh)")
							elif x == "sorry":
								if data["sid"][:int(len(data["sid"])/2)] in shamed:
									shamed.remove(data["sid"][:int(len(data["sid"])/2)])
							else:
								cprint(bcolors.YELLOW + x)
							time.sleep(0.2)
						else:
							if x is False:
								shamed.append(data["sid"][:int(len(data["sid"])/2)])
							json.dump(comm.generateData(queue, sessions, shamed), open(os.path.join(temppath, "topage.json"), "w"))
							json.dump({}, open(os.path.join(temppath, "toscript.json"), "w"), {})
					except Exception as e: 
						cprint(bcolors.YELLOW + e)
					
			time.sleep(0.01)
	except KeyboardInterrupt:
		quit(0)



if __name__ == "__main__":
	main()