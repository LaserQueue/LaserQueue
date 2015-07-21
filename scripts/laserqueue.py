import json
import uuid
import time
import os.path
from copy import deepcopy

from parseargv import args as argvs
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

class QueueObject(dict):
	def serialize(self):
		obj = dict(self)
		del obj["sec"]
		return obj
	def update(self, priority, authstate):
		self["time"] = time.time()
		self["priority"] = priority
		if authstate: self["coachmodified"] = True

class Queue:
	requiredtags = {
		"priority":0,
		"name":"DEFAULT",
		"material":"o", 
		"esttime": 0, 
		"coachmodified": False, 
		"uuid": "this object is so old that it should be deleted", 
		"sec": "this object is so old that it should be deleted", 
		"time": 2**30,
		"totaldiff": 0
	}
	def __init__(self):
		self.queue = [[] for i in config["priorities"]]

	@staticmethod
	def convert(queue):
		return [[QueueObject(j) for j in i] for i in queue]


	@classmethod
	def load(cls, fileobj):
		jdata = json.load(fileobj)
		self = cls()

		if type(jdata) is not list:
			return self
		jdata = Queue.convert(jdata)
		if len(jdata) != len(config["priorities"]):
			if len(jdata) > len(config["priorities"]):
				self.queue = jdata[:len(config["priorities"])]
			elif len(jdata) < len(config["priorities"]):
				self.queue = jdata + [[] for i in range(len(config["priorities"])-len(jdata))]
		else:
			self.queue = jdata
		for ii in range(len(self.queue)):
			i = self.queue[ii]
			for job in i:
				job["priority"] = ii
				job = QueueObject(Queue.requiredtags, **job)

		return self

	def serialize(self):
		return [[j.serialize() for j in i] for i in self.queue]

	def metapriority(self):
		for i in self.queue:
			for job in i:
				if time.time()-job["time"] > (config["metabump"] + config["metabumpmult"]*job["priority"]) and config["metabump"]:
					pri = job["priority"]-1
					maxbump = config["metabumpmax"]
					if maxbump < 0:
						maxbump = lpri
					if pri < (lpri-maxbump):
						job["time"] = time.time()
						continue
					i.remove(job)
					job["time"] += config["metabump"] + config["metabumpmult"]*job["priority"]
					job["priority"] = pri
					self.queue[pri].append(job)

	def getQueueObject(self, u):
		target = None
		masterqueue = self.masterqueue()
		for i in self.queue:
				for j in i:
					if j["uuid"] == u:
						target = j
						target_index = masterqueue.index(target)
						target_priority = self.queue.index(i)
						target_internal_index = i.index(target)
						break
		if not target:
			raise ValueError("No such tag!")
		return target, target_index, target_priority, target_internal_index

	def getQueueData(self, job):
		_, target_index, target_priority, target_internal_index = self.getQueueObject(job["uuid"])
		return target_index, target_priority, target_internal_index

	def masterqueue(self):
		return _concatlist(self.queue[::-1])

	def append(self, **kwargs):
		args, authstate, sec = kwargs["args"], kwargs["authstate"], kwargs["sec"]
		name, priority, esttime, material = args["name"], args["priority"], args["time"], args["material"]
		if not name or material == "N/A" or priority == -1:
			return

		bounds = config["length_bounds"]
		if bounds[0] >= 0:
			esttime = max(bounds[0], esttime)
		if bounds[1] >= 0:
			esttime = min(bounds[1], esttime)

		if not config["priority_selection"] and not authstate:
			priority = min(config["default_priority"], priority)

		if config["recalc_priority"]:
			priority = _calcpriority(priority, esttime)

		name = name.strip().rstrip()

		inqueue = False
		for i in self.queue:
			for j in i: 
				if name.lower() == j["name"].lower() and (
						material == j["material"] or (
						not config["allow_multiple_materials"])):
					inqueue = True
					break

		if config["recapitalize"]:
			name = name.title()

		job_uuid = str(uuid.uuid1())

		if not inqueue or config["allow_multiples"]:
			color = bcolors.MAGENTA if authstate else ""
			cprint("Added {} to the queue.\n({})".format(name, job_uuid), color=color)
			self.queue[priority].append(QueueObject({
				"totaldiff": 0,
				"priority": priority,
				"name": name,
				"material": material,
				"esttime": esttime,
				"coachmodified": authstate,
				"uuid": job_uuid,
				"sec": sec,
				"time": time.time()
			}))

	def remove(self, **kwargs):
		args = kwargs["args"]
		u = args["uuid"]
		job, masterindex, priority, index = self.getQueueObject(u)
		self.queue[priority].remove(job)
		if argvs.loud:
			color = bcolors.MAGENTA if authstate else ""
			cprint("Removed {} from the queue.\n({})".format(job["name"], job["uuid"]), color=color)

	def passoff(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		u = args["uuid"]
		job, masterindex, priority, index = self.getQueueObject(u)

		masterqueue = self.masterqueue()

		pass_depth = min(len(masterqueue)-1, config["pass_depth"])

		if masterindex >= len(masterqueue)-1: return
		if masterindex >= config["pass_depth"] and not authstate: return

		self.queue[priority].remove(job)

		endtarget = masterqueue[masterindex+1]
		new_masterindex, new_priority, new_index = self.getQueueData(endtarget)

		job.update(new_priority, authstate)
		self.queue[new_priority].insert(new_index+1, job)

		if argvs.loud:
			color = bcolors.MAGENTA if authstate else ""
			cprint("Passed {} down the queue.\n({})".format(job["name"], job["uuid"]), color=color)


	def relmove(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		u, nindex = args["uuid"], args["target_index"]
		masterqueue = self.masterqueue()

		if len(masterqueue) <= 1: return

		job, masterindex, priority, index = self.getQueueObject(u)
		self.queue[priority].remove(job)

		masterqueue = self.masterqueue()
		if nindex <= 0:
			bpri = masterqueue[0]["priority"]
			bind = 0
		elif nindex >= len(masterqueue):
			bpri = masterqueue[-1]["priority"]
			bind = len(self.queue[bpri])
		else:
			btarget = masterqueue[nindex-1]
			_, bpri, bind = self.getQueueData(btarget)
			bind += 1

		job.update(bpri, authstate)
		self.queue[bpri].insert(bind, job)

		if argvs.loud:
			color = bcolors.MAGENTA if authstate else ""
			cprint("Moved {} from position {} to {}.\n({})".format(
				job["name"], masterindex, nindex, job["uuid"]), color=color)


	def move(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		u, ni, np = args["uuid"], args["target_index"], args["target_priority"]

		job, masterindex, priority, index = self.getQueueObject(u)
		self.queue[priority].remove(job)

		job.update(np, authstate)
		self.queue[np].insert(ni, job)

		if argvs.loud:
			color = bcolors.MAGENTA if authstate else ""
			cprint("Moved {} to index {} within priority {}.\n({})".format(
				job["name"], ni, np, job["uuid"]), color=color)

	def increment(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		u = args["uuid"]

		job, masterindex, priority, index = self.getQueueObject(u)
		if priority == lpri and not index:
			return
		self.queue[priority].remove(job)

		index -= 1
		if index < 0:
			priority += 1
			if priority > lpri:
				index = 0
				priority = lpri
			else:
				index = len(self.queue[min(priority, lpri)])

		priority = min(priority, lpri)
		index = min(index, len(self.queue[priority]))
		job.update(priority, authstate)
		self.queue[priority].insert(index, job)

		if argvs.loud:
			color = bcolors.MAGENTA if authstate else ""
			cprint("Moved {} from position {} to {}.\n({})".format(
				job["name"], masterindex, masterindex - 1, job["uuid"]), color=color)

	def decrement(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		u = args["uuid"]

		job, masterindex, priority, index = self.getQueueObject(u)
		if not priority and len(self.queue[priority]) <= index:
			return
		self.queue[priority].remove(job)

		index += 1
		if len(self.queue[priority]) < index:
			priority -= 1
			if priority < 0:
				index = len(self.queue[max(priority, 0)])
				priority = 0
			else:
				index = 0
		priority = max(priority, 0)
		index = max(index, 0)
		job.update(priority, authstate)
		self.queue[priority].insert(index ,job)

		if argvs.loud:
			color = bcolors.MAGENTA if authstate else ""
			cprint("Moved {} from position {} to {}.\n({})".format(
				job["name"], masterindex, masterindex + 1, job["uuid"]), color=color)

	def attr(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		u, attrname, value = args["uuid"], args["key"], args["new"]

		if attrname not in self.requiredtags or attrname in ["uuid", "sec", "time", "totaldiff", "priority"]:
			return "Cannot change the `{}` value of a job.".format(attrname)
		if attrname not in config["attr_edit_perms"] and not authstate:
			return "Changing a job's `{}` value requires auth.".format(attrname)

		job, masterindex, priority, index = self.getQueueObject(u)

		oldval = job[attrname]

		if attrname not in config["attr_edit_perms"] and attrname != "coachmodified":
			job["coachmodified"] = True

		if attrname == "name": 
			job["name"] = str(value).strip().rstrip()

		elif attrname == "material" and value in config["materials"]: 
			job["material"] = value

		elif attrname == "esttime":
			bounds = config["length_bounds"]
			if bounds[0] >= 0:
				value = max(bounds[0], value)
			if bounds[1] >= 0:
				value = min(bounds[1], value)
			prevtime = job["esttime"]
			job["esttime"] = value
			if config["recalc_priority"] and not authstate:
				newpriority = priority*1
				job["totaldiff"] += value-prevtime
				job["totaldiff"] = max(job["totaldiff"], 0)
				while job["totaldiff"] >= 10: 
					newpriority -= 1
					job["totaldiff"] -= 10

				newpriority = max(newpriority, 0)
				job["priority"] = newpriority
				if priority != newpriority:
					self.queue[priority].pop(index)
					self.queue[newpriority].append(job)
			elif authstate and config["recalc_priority"]:
				job["coachmodified"] = True

		elif attrname == "coachmodified": 
			job["coachmodified"] = bool(value)

		if argvs.loud:
			newval = job[attrname]
			color = bcolors.MAGENTA if authstate else ""
			cprint("Changed {}'s `{}` value from {} to {}.\n({})".format(
				job["name"], attrname, oldval, newval, job["uuid"]), color=color)

