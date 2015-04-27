from queue import Queue, config
import jsonhandler as comm

import json
import os.path

calculated_time = 0 # Compat with windows version
elapsed_time = 0    # Compat with windows version

def main():
	global calculated_time, elapsed_time
	queue = Queue()
	temppath = os.path.join(os.path.sep, "tmp")

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

	

if __name__ == "__main__":
	main()