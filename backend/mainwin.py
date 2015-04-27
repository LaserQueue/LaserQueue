from laserqueue import Queue, config
import getesttime as estimate
# import getlasertime as elapsed
import jsonhandler as comm

import json
import time
import threading
import os.path

calculated_time = 0
def getestimate():
	global calculated_time
	while True:
		if estimate._dlexists():
			calculated_time = estimate.ondownloadpressed()

elapsed_time = 0
# def getelapsed():
# 	global elapsed_time
# 	while True:
# 		elapsed_time = elapsed.read()

def main():
	global calculated_time, elapsed_time
	queue = Queue()
	estimateT = threading.Thread(target=getestimate)
	# elapsedT = threading.Thread(target=getelapsed)
	estimateT.start()
	# elapsedåT.start()
	temppath = os.path.expanduser(os.path.join("~", "AppData", "Local", "Temp"))
	lelap, lcalc = elapsed_time, calculated_time

	json.dump({}, open(os.path.join(temppath, "toscript.json"), "w"))

	while True:
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
					print("not valid packet")
			if data:
				try:
					comm.parseData(queue, data)
				except: pass
				json.dump(comm.generateData(queue, calculated_time, elapsed_time), open(os.path.join(temppath, "topage.json"), "w"))
				json.dump({}, open(os.path.join(temppath, "toscript.json"), "w"), {})
				if data["action"] != "null": print(queue.queue)
		elif lelap != elapsed_time or lcalc != calculated_time:
			json.dump(open(os.path.join(temppath, "topage.json"), "w"), comm.generateData(queue, calculated_time, elapsed_time))

	

if __name__ == "__main__":
	main()