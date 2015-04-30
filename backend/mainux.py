from laserqueue import Queue, config
import jsonhandler as comm

import json
import os.path
import time

import argparse
parser = argparse.ArgumentParser(add_help=False)
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

	stamp = time.time()
	while True:
		if time.time()-stamp > 20 and args.backup:
			stamp = time.time()
			json.dump(queue.queue, open("cache.json", "w"))
			print("queue backed up")
		if os.path.exists(os.path.join(temppath, "toscript.json")):
			dataf = open(os.path.join(temppath, "toscript.json"))
			datat = dataf.read()
			try:
				data = json.loads(datat)
				if data and data["action"] != null:
					print(data)
			except:
				if "action" in data and data["action"] != "null":
					print(datat)
			if data:
				try:
					x = comm.parseData(queue, data)
					if x:
						json.dump({"action":"notification", "title":"Error occurred", "content":x}, open(os.path.join(temppath, "topage.json"), "w"))
						time.sleep(0.2)
				except: 
					pass
				json.dump(comm.generateData(queue, calculated_time, elapsed_time), open(os.path.join(temppath, "topage.json"), "w"))
				json.dump({}, open(os.path.join(temppath, "toscript.json"), "w"), {})
				if data["action"] != "null": print(queue.queue)

	

if __name__ == "__main__":
	main()