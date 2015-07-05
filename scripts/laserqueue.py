import json
import uuid
import time
import os.path
from copy import deepcopy

from config import *
config = Config(os.path.join("..","www","config.json"))

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

def _fillblanks(odict, adict):
	return dict(adict, **odict)

class Queue:
	requiredtags = {
		"priority":0,
		"name":"DEFAULT",
		"material":"o", 
		"esttime": 0, 
		"coachmodified": False, 
		"uuid": "this object is so old that it should be deleted", 
		"sid": "this object is so old that it should be deleted", 
		"time": 2**30,
		"totaldiff": 0
	}
	def __init__(self):
		self.queue = [[] for i in config["priorities"]]

	@classmethod
	def load(cls, fileobj):
		jdata = json.load(fileobj)
		self = cls()
		if type(jdata) is not list:
			return self
		if len(jdata) != len(config["priorities"]):
			if len(jdata) > len(config["priorities"]):
				self.queue = jdata[:len(config["priorities"])]
			elif len(jdata) < len(config["priorities"]):
				self.queue = jdata + [[] for i in range(len(config["priorities"])-len(jdata))]
		else:
			self.queue = jdata
		for ii in range(len(self.queue)):
			i = self.queue[ii]
			for item in i:
				item["priority"] = ii
				item = _fillblanks(item, Queue.requiredtags)
		return self

	def metapriority(self):
		for i in self.queue:
			for item in i:
				if time.time()-item["time"] > (config["metabump"] + config["metabumpmult"]*item["priority"]) and config["metabump"]:
					pri = item["priority"]-1
					if pri < 0:
						item["time"] = time.time()
						continue
					i.remove(item)
					item["time"] += config["metabump"] + config["metabumpmult"]*item["priority"]
					item["priority"] = pri
					self.queue[pri].append(item)


	def append(self, **kwargs):
		args, authstate, sid = kwargs["args"], kwargs["authstate"], kwargs["sid"]
		name, priority, esttime, material = args[0], args[1], args[2], args[3]
		if not name or material == "N/A" or priority == -1:
			return
		bounds = config["length_bounds"]
		if bounds[0] >= 0:
			esttime = max(bounds[0], esttime)
		if bounds[1] >= 0:
			esttime = min(bounds[1], esttime)

		if not config["priority_selection"] and not authstate:
			priority = min(lpri-config["default_priority"], priority)

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
				"totaldiff": 0,
				"priority": lpri-priority,
				"name": name.strip().rstrip(),
				"material": material,
				"esttime": esttime,
				"coachmodified": authstate,
				"uuid": str(uuid.uuid1()),
				"sid": sid,
				"time": time.time()
			})

	def remove(self, **kwargs):
		args = kwargs["args"]
		u = args[0]
		for i in self.queue:
			for j in i:
				if j["uuid"] == u:
					i.remove(j)
	def passoff(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		u = args[0]
		oindex = -1
		masterqueue = _concatlist(self.queue)
		for i in self.queue:
			for j in i:
				if j["uuid"] == u:
					oindex = masterqueue.index(j)
		if oindex == -1: return
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
		target["time"] = time.time()
		target["priority"] = lpri-tpri
		if authstate: target["coachmodified"] = True
		self.queue[lpri-tpri].insert(tindex+1, target)

	def relmove(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		u, nindex = args[0], args[1]
		target = None
		masterqueue = _concatlist(self.queue)
		if len(masterqueue) <= 1: return
		for i in self.queue:
			for j in i:
				if j["uuid"] == u:
					target = deepcopy(j)
					i.remove(j)
		if not target: return

		masterqueue = _concatlist(self.queue)

		if nindex <= 0:
			bpri = masterqueue[0]["priority"]
			bind = 0
		elif nindex >= len(masterqueue):
			bpri = masterqueue[-1]["priority"]
			bind = len(self.queue[bpri])
		else:
			btarget = masterqueue[nindex-1]
			bpri = btarget["priority"]
			bind = self.queue[bpri].index(btarget)+1

		target["time"] = time.time()
		target["priority"] = bpri
		if authstate: target["coachmodified"] = True
		self.queue[bpri].insert(bind, target)


	def move(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		u, ni, np = args[0], args[1], args[2]
		target = None
		for i in self.queue:
			for j in i:
				if j["uuid"] == u:
					target = deepcopy(j)
					i.remove(j)
		if not target: return
		target["time"] = time.time()
		if authstate: target["coachmodified"] = True
		target["priority"] = lpri-np
		self.queue[lpri-np].insert(ni, target)

	def increment(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		u = args[0]
		index = -1
		priority = -1
		for i in self.queue:
			for j in i:
				if j["uuid"] == u:
					index = i.index(j)
					priority = lpri-self.queue.index(i)
		if index == -1 and priority == -1: return
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
		item["time"] = time.time()
		if authstate: item["coachmodified"] = True
		item["priority"] = lpri-priority
		self.queue[max(lpri-priority, 0)].insert(min(index, len(self.queue[max(lpri-priority, 0)])),item)

	def decrement(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		u = args[0]
		index = -1
		priority = -1
		for i in self.queue:
			for j in i:
				if j["uuid"] == u:
					index = i.index(j)
					priority = lpri-self.queue.index(i)
		if index == -1 and priority == -1: return
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
		item["time"] = time.time()
		if authstate: item["coachmodified"] = True
		item["priority"] = lpri-priority
		self.queue[min(lpri-priority, lpri)].insert(max(index, 0),item)

	def attr(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		u, attrname, value = args[0], args[1], args[2]
		if attrname not in self.requiredtags or attrname in ["uuid", "sid", "time", "totaldiff"]:
			return
		if attrname not in config["attr_edit_perms"] and not authstate:
			return
		index = -1
		priority = -1
		for i in self.queue:
			for j in i:
				if j["uuid"] == u:
					index = i.index(j)
					priority = lpri-self.queue.index(i)
		if index == -1 and priority == -1: return
		item = self.queue[lpri-priority][index]
		if attrname not in config["attr_edit_perms"] and attrname != "coachmodified":
			item["coachmodified"] = True

		if attrname == "name": item["name"] = str(value).strip().rstrip()
		elif attrname == "material" and value in config["materials"]: item["material"] = value
		elif attrname == "esttime":
			bounds = config["length_bounds"]
			if bounds[0] >= 0:
				value = max(bounds[0], value)
			if bounds[1] >= 0:
				value = min(bounds[1], value)
			prevtime = item["esttime"]
			item["esttime"] = value
			if config["recalc_priority"] and not authstate:
				newpriority = priority*1
				item["totaldiff"] += value-prevtime
				item["totaldiff"] = max(item["totaldiff"], 0)
				while item["totaldiff"] >= 10: 
					newpriority -= 1
					item["totaldiff"] -= 10

				newpriority = max(newpriority, 0)
				item["priority"] = lpri-newpriority
				self.queue[lpri-priority].pop(index)
				self.queue[lpri-newpriority].append(item)
			elif authstate and config["recalc_priority"]:
				item["coachmodified"] = True
		elif attrname == "coachmodified": item["coachmodified"] = bool(value)

