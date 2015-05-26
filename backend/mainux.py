from laserqueue import Queue, config
import jsonhandler as comm
import sidhandler as sids

import json
import os.path
import time

import argparse
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-l", "--local", help="Run from localhost", dest="local",
	action="store_const",const=True,default=False)
parser.add_argument("-p", "--port", help="Port to host from", dest="port",
	default=80, type=int)
parser.add_argument("-n", "--regen-host", help="Regenerate host in config", dest="host",
	action="store_const",const=True,default=False)
parser.add_argument("-b", "--queue-backup", help="Backup queue and load from backup on start", dest="backup",
	action="store_const",const=True,default=False)
parser.add_argument("-h", "--help", help="Show help", dest="help",
	action="store_const",const=True,default=False)
parser.add_argument("-r", "--regen-config", help="Regenerate config.json", dest="regen",
	action="store_const",const=True,default=False)
parser.add_argument("-s", "--skip-install", help="Skip package installation", dest="skip",
	action="store_const",const=True,default=False)
parser.add_argument("--install-all", help="Don't ask for confirmation on install", dest="all",
	action="store_const",const=True,default=False)
args = parser.parse_args()
if args.help:
	quit()

calculated_time = -1 # Compat with windows version
elapsed_time = -1    # Compat with windows version

def main():
	global calculated_time, elapsed_time
	queue = Queue()
	temppath = os.path.join(os.path.sep, "tmp")

	json.dump({}, open(os.path.join(temppath, "toscript.json"), "w"))

	if args.backup:
		if os.path.exists("cache.json"):
			queue.queue = json.load(open("cache.json"))
		sessions = sids.loadcache()
	else:
		sessions = sids.SIDCache()

	stamp = time.time()
	while True:
		if os.path.exists(os.path.join(temppath, "toscript.json")):
			dataf = open(os.path.join(temppath, "toscript.json"))
			datat = dataf.read()
			if datat and datat != "{}":
				data = json.loads(datat)
				try:
					x = comm.parseData(queue, sessions, data)
					if "action" in data and data["action"] != "null":
						print(json.dumps(data, indent=2))
						if args.backup:
							json.dump(queue.queue, open("cache.json", "w"), indent=2)
							sids.cache(sessions)
					if x:
						print(x)
						if x == "uuddlrlrba" and config["easter_eggs"]:
							json.dump({"action":"rickroll"}, open(os.path.join(temppath, "topage.json"), "w"))
							time.sleep((config["refreshRate"]*1.5)/1000)
						time.sleep(0.2)
					else:
						json.dump(comm.generateData(queue, calculated_time, elapsed_time), open(os.path.join(temppath, "topage.json"), "w"))
						json.dump({}, open(os.path.join(temppath, "toscript.json"), "w"), {})
						if data["action"] != "null": print(queue.queue)
				except: 
					pass
				
		time.sleep(0.01)

	

if __name__ == "__main__":
	main()