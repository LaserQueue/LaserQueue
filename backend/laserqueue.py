import json
import uuid
import time
import os.path
from copy import deepcopy

config = json.load(open(os.path.join("..", "www", "config.json")))

lpri = len(config["priorities"])-1

def _calcpriority(priority, time):
	for i in config["priority_thresh"]:
		if time >= i:
			priority -= 1
	return max(priority, 0)

def _concatlist(lists):
	masterlist = []
	for i in lists: 
		for j in i:
			masterlist.append(j)
	return masterlist

def _fillblanks(odict, keys):
	for i in keys:
		if i not in odict:
			odict[i] = None
	return odict

class Queue:
	requiredtags = ["priority", "name", "material", "esttime", "coachmodified", "uuid", "sid", "time"]
	def __init__(self):
		self.queue = [[] for i in config["priorities"]]

	def load(fileobj): # init method, do not call on existing object
		jdata = json.load(fileobj)
		q = Queue()
		if type(jdata) is not list:
			return q
		if len(jdata) != len(config["priorities"]):
			if len(jdata) > len(config["priorities"]):
				q.queue = jdata[:len(config["priorities"])]
			elif len(jdata) < len(config["priorities"]):
				q.queue = jdata + [[] for i in range(len(config["priorities"])-len(jdata))]
		else:
			q.queue = jdata
		for ii in range(len(q.queue)):
			i = q.queue[ii]
			for item in i:
				item["priority"] = ii
				item = _fillblanks(item, Queue.requiredtags)
		return q

	def metapriority(self):
		for i in self.queue:
			for item in i:
				if time.time()-item["time"] > (config["metabump"] + config["metabumpmult"]*item["priority"]):
					pri = item["priority"]-1
					if pri < 0:
						item["time"] = time.time()
						continue
					i.remove(item)
					item["time"] += config["metabump"] + config["metabumpmult"]*item["priority"]
					item["priority"] = pri
					self.queue[pri].append(item)


	def append(self, name, priority, esttime, material, sid, authstate):
		if not name:
			return
		bounds = config["length_bounds"]
		if bounds[0] >= 0:
			esttime = max(bounds[0], esttime)
		if bounds[1] >= 0:
			esttime = min(bounds[1], esttime)

		if config["recalc_priority"]:
			priority = _calcpriority(priority, esttime)

		inqueue = False
		for i in self.queue:
			for j in i: 
				if name.lower() == j["name"].lower() and (material == j["material"] or not config["allow_multiple_materials"]):
					inqueue = True
					break

		if config["recapitalize"]:
			name = name.title()

		if not inqueue or config["allow_multiples"]:
			self.queue[lpri-priority].append({
				"priority": lpri-priority,
				"name": name.strip().rstrip(),
				"material": material,
				"esttime": esttime,
				"coachmodified": authstate,
				"uuid": str(uuid.uuid1()),
				"sid": sid,
				"time": time.time()
			})

	def passoff(self, priority, index=0):
		if not priority and len(self.queue[lpri-priority]) < index:
			return
		item = self.queue[lpri-priority].pop(index)
		index += 1
		if len(self.queue[lpri-priority]) < index:
			priority -= 1
			index = 0
		item["priority"] = lpri-priority
		self.queue[lpri-priority].insert(max(index, 0),item)
		
	def move(self, in1, in2, pr1, pr2):
		item = self.queue[lpri-pr1].pop(in1)
		item["coachmodified"] = True
		item["priority"] = lpri-priority
		if in2 >= 0:
			self.queue[lpri-pr2].insert(in2, item)
		else:
			self.queue[lpri-pr2].append(item)
	def remove(self, priority, index):

		del self.queue[lpri-priority][index]
	def sremove(self, index):
		masterqueue = _concatlist(self.queue)
		target = masterqueue[index] 
		for i in self.queue:
			if target in i:
				i.remove(target)
	def spass(self, oindex):
		masterqueue = _concatlist(self.queue)
		if oindex == len(masterqueue)-1: return
		target = masterqueue[oindex]
		for ii in range(len(self.queue)):
			i = self.queue[ii]
			if target in i:
				i.remove(target)
		end = masterqueue[oindex+1]
		for ii in range(len(self.queue)):
			i = self.queue[ii]
			if end in i:
				tindex = i.index(end)
				tpri = lpri-ii
		target["priority"] = lpri-tpri
		self.queue[lpri-tpri].insert(tindex+1, target)

	def smove(self, oi, ni, np):
		masterqueue = _concatlist(self.queue)
		target = masterqueue[oi]
		for i in self.queue:
			if target in i:
				i.remove(target)
		target["coachmodified"] = True
		target["priority"] = lpri-np
		self.queue[lpri-np].insert(ni, target)

	def sincrement(self, index):
		masterqueue = _concatlist(self.queue)
		target = masterqueue[index] 
		for ii in range(len(self.queue)):
			i = self.queue[ii]
			if target in i:
				index = i.index(target)
				priority = lpri-ii

		if priority == lpri and not index:
			return
		item = self.queue[lpri-priority].pop(index)
		index -= 1
		if index < 0:
			priority += 1
			if priority > lpri:
				index = 0
				priority = lpri
			else:
				index = len(self.queue[max(lpri-priority, 0)])
		item["coachmodified"] = True
		item["priority"] = lpri-priority
		self.queue[max(lpri-priority, 0)].insert(min(index, len(self.queue[max(lpri-priority, 0)])),item)

	def sdecrement(self, index):
		masterqueue = _concatlist(self.queue)
		target = masterqueue[index] 
		for ii in range(len(self.queue)):
			i = self.queue[ii]
			if target in i:
				index = i.index(target)
				priority = lpri-ii

		if not priority and len(self.queue[lpri-priority]) < index:
			return
		item = self.queue[lpri-priority].pop(index)
		index += 1
		if len(self.queue[lpri-priority]) < index:
			priority -= 1
			if priority < 0:
				index = len(self.queue[min(lpri-priority, lpri)])
				priority = 0
			else:
				index = 0
		item["coachmodified"] = True
		item["priority"] = lpri-priority
		self.queue[min(lpri-priority, lpri)].insert(max(index, 0),item)
	
	# uuid update




	def uremove(self, u):
		for i in self.queue:
			for j in i:
				if j["uuid"] == u:
					i.remove(j)
	def upass(self, u):
		masterqueue = _concatlist(self.queue)
		for i in self.queue:
			for j in i:
				if j["uuid"] == u:
					oindex = masterqueue.index(j)

		if oindex == len(masterqueue)-1: return
		target = masterqueue[oindex]
		for ii in range(len(self.queue)):
			i = self.queue[ii]
			if target in i:
				i.remove(target)
		end = masterqueue[oindex+1]
		for ii in range(len(self.queue)):
			i = self.queue[ii]
			if end in i:
				tindex = i.index(end)
				tpri = lpri-ii
		target["priority"] = lpri-tpri
		self.queue[lpri-tpri].insert(tindex+1, target)

	def umove(self, u, ni, np):
		for i in self.queue:
			for j in i:
				if j["uuid"] == u:
					target = deepcopy(j)
					i.remove(j)
		target["coachmodified"] = True
		target["priority"] = lpri-np
		self.queue[lpri-np].insert(ni, target)

	def uincrement(self, u):
		for i in self.queue:
			for j in i:
				if j["uuid"] == u:
					index = j.index(i)
					priority = self.queue.index(i)

		if priority == lpri and not index:
			return
		item = self.queue[lpri-priority].pop(index)
		index -= 1
		if index < 0:
			priority += 1
			if priority > lpri:
				index = 0
				priority = lpri
			else:
				index = len(self.queue[max(lpri-priority, 0)])
		item["coachmodified"] = True
		item["priority"] = lpri-priority
		self.queue[max(lpri-priority, 0)].insert(min(index, len(self.queue[max(lpri-priority, 0)])),item)

	def udecrement(self, u):
		for i in self.queue:
			for j in i:
				if j["uuid"] == u:
					index = j.index(i)
					priority = self.queue.index(i)

		if not priority and len(self.queue[lpri-priority]) < index:
			return
		item = self.queue[lpri-priority].pop(index)
		index += 1
		if len(self.queue[lpri-priority]) < index:
			priority -= 1
			if priority < 0:
				index = len(self.queue[min(lpri-priority, lpri)])
				priority = 0
			else:
				index = 0
		item["coachmodified"] = True
		item["priority"] = lpri-priority
		self.queue[min(lpri-priority, lpri)].insert(max(index, 0),item)
