import json
import uuid
import time
import os.path
from copy import deepcopy

from parseargv import args as argvs
from config import *
config = Config(CONFIGDIR)

maximum_priority = len(config["priorities"])-1

def _calcpriority(priority, time):
	"""
	Recalculate priority values from `time`.
	"""
	for i in config["priority_thresh"]:
		if time >= i:
			priority -= 1
	return max(priority, 0)

def _concatlist(lists):
	"""
	Return the sum of each iterable in `lists`.
	"""
	masterlist = []
	for i in lists: 
		for j in i:
			masterlist.append(j)
	return masterlist

# Tags which need to exist in a queue object.
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

# Tags which will not be sent to the client.
hideFromClient = [
	"sec"
]

def buildLists(modules):
	global requiredtags, hideFromClient
	for module in modules:
		if hasattr(module, "requiredTags"):
			requiredtags = dict(d, **module.requiredTags)
		if hasattr(module, "hideFromClient"):
			hideFromClient += module.hideFromClient

class QueueObject(dict):
	"""
	An extension to `dict` that has special methods for queue manipulation.
	"""

	def __init__(self, maindict, *args, **kwargs):
		"""
		Initialize this class using requiredtags as a base.
		"""
		global requiredtags
		kwargs = dict(maindict, **kwargs)
		kwargs = dict(requiredtags, **kwargs)
		super(self.__class__, self).__init__(*args, **kwargs)

	@classmethod
	def convert(cls, queue):
		"""
		Converts `queue` to QueueObjects from dicts.
		"""
		return [[cls(j) for j in i] for i in queue]

	def serialize(self):
		"""
		Returns a version of this object without the Sec-key, which shouldn't be sent to clients.
		"""
		global hideFromClient
		obj = dict(self)
		for i in hideFromClient:
			del obj[i]
		return obj

	def update(self, priority, authstate=False):
		"""
		Updates priority, timestamp, and the coach gear if applicable.
		"""
		self["time"] = time.time()
		self["priority"] = priority
		if authstate: self["coachmodified"] = True

class Queue:
	"""
	A queue class that stores a 2 dimensional array of jobs.
	The first dimension is priority, and the second dimension precedence within that priority.
	"""
	def __init__(self):
		"""
		Set up a blank queue.
		"""
		self.queue = [[] for i in config["priorities"]]

	@classmethod
	def load(cls, fileobj):
		"""
		Load a queue from a file-like object.
		"""
		jdata = json.load(fileobj)
		self = cls() # Get an empty queue
		if type(jdata) is not list:
			return self # Return an empty object if the type isn't right
		jdata = QueueObject.convert(jdata) # Read the jdata

		# If there are too many priorities, cut off the end ones
		if len(jdata) > len(config["priorities"]): 
			self.queue = jdata[:len(config["priorities"])]
		# If there are too few priorities, add on more to the end
		elif len(jdata) < len(config["priorities"]): 
			discrepancy = len(config["priorities"]) - len(jdata) 
			self.queue = jdata + [[] for i in range(discrepancy)]
		else:
			self.queue = jdata

		# Ensure correct priorities
		for ii in range(len(self.queue)):
			i = self.queue[ii]
			for job in i: 
				job["priority"] = ii
		return self

	def serialize(self):
		"""
		Serialize the queue for sending to clients.
		"""
		return [[j.serialize() for j in i] for i in self.queue]

	def metapriority(self):
		"""
		Run through the queue and update priorities that have been waiting for a long time.
		"""
		if not config["metabump"]: # If metabumping is disabled, stop the process
			return

		for i in self.queue:
			for job in i:
				# If enough time has passed to overtake the threshold, bump upwards
				if time.time()-job["time"] > (config["metabump"] + config["metabumpmult"]*job["priority"]):
					# Increment priority
					pri = job["priority"]+1

					# The maximum priority that can be bumped to, which can't be higher than the true maximum
					maxbump = min(config["metabumpmax"], maximum_priority)
					if maxbump < 0:
						maxbump = maximum_priority

					# If the priority is high enough it can't be bumped further, reset the timestamp and pass by
					if pri > maxbump:
						job["time"] = time.time()
						continue

					# Bump the object upwards, and reset the timestamp
					i.remove(job)
					job["time"] += config["metabump"] + config["metabumpmult"]*job["priority"]
					job["priority"] = pri
					self.queue[pri].append(job)

	def getQueueObject(self, job_uuid, graceful = False):
		"""
		Get a queue object by `job_uuid`.
		"""
		target = None
		masterqueue = self.masterqueue()
		# Iterate through the queue until job_uuid is found
		for i in self.queue:
				for j in i:
					if j["uuid"] == job_uuid:
						target = j
						# Extract data about the target
						target_index = masterqueue.index(target)
						target_priority = self.queue.index(i)
						target_internal_index = i.index(target)
						break

		# If it was never found, raise an error
		if not target:
			if graceful:
				return None, None, None, None
			raise ValueError("No such tag: {}".format(job_uuid))

		return target, target_index, target_priority, target_internal_index

	def getQueueData(self, job, graceful = False):
		"""
		Get a queue object that's similar to `job`
		"""
		# Extract `job`'s uuid and use it with getQueueObject, and return the results
		_, target_index, target_priority, target_internal_index = self.getQueueObject(job["uuid"], graceful)
		return target_index, target_priority, target_internal_index

	def masterqueue(self):
		"""
		Get the masterqueue. (the same ordering as rendered by the frontend)
		"""
		return _concatlist(self.queue[::-1])

	# All functions beyond this point are socket-type functions.
	# See API.md for info on what to pass as `args`.

	# Other requirements: 
	# `authstate`: a boolean that contains whether the session is authenticated.
	# `sec`: the identifier for the session, used to change/get its authstate.
	# `sessions`: the global instance of sidhandler.SIDCache.
	# `ws`: the websocket for this session.
	# `sockets`: a main.Sockets object that contains all the current sessions.

	def append(self, **kwargs):
		"""
		Adds an object to the queue.
		"""
		args, authstate, sec, ws = kwargs["args"], kwargs["authstate"], kwargs["sec"], kwargs["ws"]
		name, priority, esttime, material = args["name"], args["priority"], args["time"], args["material"]

		# If the priority or the material aren't set up, or the name isn't defined
		if not name or material == "N/A" or priority == -1:
			# Tell the client then don't add the object
			serveToConnection({
				"action": "notification",
				"title": "Incomplete data",
				"text": "Please fill out the submission form fully."
				}, ws)
			if argvs.loud:
				cprint("Insufficient data to add job to queue.", color=bcolors.YELLOW)
			return

		# Contain the length of time within the configurable bounds.
		bounds = config["length_bounds"]
		if bounds[0] >= 0:
			esttime = max(bounds[0], esttime)
		if bounds[1] >= 0:
			esttime = min(bounds[1], esttime)

		# lock the priority down to the max if the user isn't authed.
		if not config["priority_selection"] and not authstate:
			priority = min(config["default_priority"], priority)

		# Recalculate priority if applicable.
		if config["recalc_priority"]:
			priority = _calcpriority(priority, esttime)

		# Strip whitespace from the name and recapitalize it
		name = name.strip().rstrip()
		if config["recapitalize"]:
			name = name.title()

		# Make sure the user isn't in the queue. The config can allow multiple materials per person, or not.
		inqueue = False
		for i in self.queue:
			for j in i: 
				if name.lower() == j["name"].lower() and (
						material == j["material"] or (not config["allow_multiple_materials"])):
					inqueue = True
					break

		# Make the uuid of the job
		job_uuid = str(uuid.uuid1())

		if not inqueue or config["allow_multiples"]: # If the job is allowed to be created
			# Add it to the queue
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

			if argvs.loud: # If -v, report success
				color = bcolors.MAGENTA if authstate else ""
				cprint("Added {} to the queue.\n({})".format(name, job_uuid), color=color)
		elif argvs.loud: # If -v, report failures
			cprint("Cannot add {} to the queue.".format(name), color=bcolors.YELLOW)

	def remove(self, **kwargs):
		"""
		Removes an object from the queue.
		"""
		args, authstate = kwargs["args"], kwargs["authstate"]
		job_uuid = args["uuid"]
		# Fetch the job from the queue and remove it
		job, masterindex, priority, index = self.getQueueObject(job_uuid)
		self.queue[priority].remove(job)

		if argvs.loud: # if -v, report success
			color = bcolors.MAGENTA if authstate else ""
			cprint("Removed {} from the queue.\n({})".format(job["name"], job["uuid"]), color=color)

	def passoff(self, **kwargs):
		"""
		Move the job down one. Equivalent to relmove with an index shift of 1.
		"""
		args, authstate = kwargs["args"], kwargs["authstate"]
		job_uuid = args["uuid"]
		# Fetch the job from the queue
		job, masterindex, priority, index = self.getQueueObject(job_uuid)

		masterqueue = self.masterqueue()
		# Get the maximum depth for passing
		pass_depth = min(len(masterqueue)-1, config["pass_depth"])

		# If the pass can't happen, return
		if masterindex >= len(masterqueue)-1: return
		if masterindex >= config["pass_depth"] and not authstate: 
			cprint("Passing at this depth requires auth.", color=bcolors.YELLOW)
			return

		# Remove the job
		self.queue[priority].remove(job)

		# Figure out where the end target is for the job
		endtarget = masterqueue[masterindex+1]
		new_masterindex, new_priority, new_index = self.getQueueData(endtarget)

		# Update the job and reinsert
		job.update(new_priority, authstate)
		self.queue[new_priority].insert(new_index+1, job)

		if argvs.loud: # if -v, report success
			color = bcolors.MAGENTA if authstate else ""
			cprint("Passed {} down the queue.\n({})".format(job["name"], job["uuid"]), color=color)


	def relmove(self, **kwargs):
		"""
		Move an object with pass logic, using masterqueue indexes. 
		"""
		args, authstate = kwargs["args"], kwargs["authstate"]
		job_uuid, nindex = args["uuid"], args["target_index"]
		masterqueue = self.masterqueue()

		# If the masterqueue is too small to change positions, stop
		if len(masterqueue) <= 1: return

		# Fetch the object and remove it
		job, masterindex, priority, index = self.getQueueObject(job_uuid)
		self.queue[priority].remove(job)

		masterqueue = self.masterqueue()
		# If the index is too low, use the lowest index possible
		if nindex <= 0:
			btarget = masterqueue[0]
		# If the index is too high, use the highest index possible
		elif nindex >= len(masterqueue):
			btarget = masterqueue[-1]
		# Get the index for the specific position
		else:
			btarget = masterqueue[nindex-1]
		_, bpri, bind = self.getQueueData(btarget)
		bind += 1

		# Update the job and reinsert
		job.update(bpri, authstate)
		self.queue[bpri].insert(bind, job)

		if argvs.loud: # if -v, report success
			color = bcolors.MAGENTA if authstate else ""
			cprint("Moved {} from position {} to {}.\n({})".format(
				job["name"], masterindex, nindex, job["uuid"]), color=color)


	def move(self, **kwargs):
		"""
		Move an object to a target index and priority.
		"""
		args, authstate = kwargs["args"], kwargs["authstate"]
		job_uuid, ni, np = args["uuid"], args["target_index"], args["target_priority"]
		# Fetch object and remove
		job, masterindex, priority, index = self.getQueueObject(job_uuid)
		self.queue[priority].remove(job)
		# reinsert at target
		job.update(np, authstate)
		self.queue[np].insert(ni, job)

		if argvs.loud: # if -v, report success
			color = bcolors.MAGENTA if authstate else ""
			cprint("Moved {} to index {} within priority {}.\n({})".format(
				job["name"], ni, np, job["uuid"]), color=color)

	def increment(self, **kwargs):
		"""
		Raise an object one index. 
		If it's at the top of a priority level it will jump to the bottom of the next.
		"""
		args, authstate = kwargs["args"], kwargs["authstate"]
		job_uuid = args["uuid"]

		# Fetch the object, and make sure it's viable for incrementing.
		job, masterindex, priority, index = self.getQueueObject(job_uuid)
		if priority == maximum_priority and not index:
			return
		# Pull it out of the queue if so.
		self.queue[priority].remove(job)

		# Make sure the index and priority are viable.
		index -= 1
		if index < 0:
			priority += 1
			if priority > maximum_priority:
				index = 0
				priority = maximum_priority
			else:
				index = len(self.queue[min(priority, maximum_priority)])

		# Cap the priority and index as applicable
		priority = min(priority, maximum_priority)
		index = min(index, len(self.queue[priority]))
		# Update and reinsert job
		job.update(priority, authstate)
		self.queue[priority].insert(index, job)

		if argvs.loud: # if -v, report success
			color = bcolors.MAGENTA if authstate else ""
			cprint("Moved {} from position {} to {}.\n({})".format(
				job["name"], masterindex, masterindex - 1, job["uuid"]), color=color)

	def decrement(self, **kwargs):
		"""
		Drop an object one index. 
		If it's at the bottom of a priority level it will jump to the top of the next.
		"""
		args, authstate = kwargs["args"], kwargs["authstate"]
		job_uuid = args["uuid"]

		# Fetch the object, and make sure it's viable for decrementing.
		job, masterindex, priority, index = self.getQueueObject(job_uuid)
		if not priority and len(self.queue[priority]) <= index:
			return
		# Pull it out of the queue if so.
		self.queue[priority].remove(job)

		# Make sure the index and priority are viable.
		index += 1
		if len(self.queue[priority]) < index:
			priority -= 1
			if priority < 0:
				index = len(self.queue[max(priority, 0)])
				priority = 0
			else:
				index = 0

		# Cap the priority and index as applicable
		priority = max(priority, 0)
		index = max(index, 0)
		# Update and reinsert job
		job.update(priority, authstate)
		self.queue[priority].insert(index ,job)

		if argvs.loud: # if -v, report success
			color = bcolors.MAGENTA if authstate else ""
			cprint("Moved {} from position {} to {}.\n({})".format(
				job["name"], masterindex, masterindex + 1, job["uuid"]), color=color)

	def attr(self, **kwargs):
		args, authstate = kwargs["args"], kwargs["authstate"]
		job_uuid, attrname, value = args["uuid"], args["key"], args["new"]

		# Make sure `attrname` is allowed to be changed (no changing timestamps, etc)
		if attrname not in requiredtags or attrname in ["uuid", "sec", "time", "totaldiff", "priority"]:
			return "Cannot change the `{}` value of a job.".format(attrname)
		# Make sure the user is allowed to edit `attrname`.
		if attrname not in config["attr_edit_perms"] and not authstate:
			return "Changing a job's `{}` value requires auth.".format(attrname)

		# Fetch the job and cache the old value of `attrname`
		job, masterindex, priority, index = self.getQueueObject(job_uuid)
		oldval = job[attrname]

		# Add coachmodified tag if you're not setting it with `attrname`
		if attrname not in config["attr_edit_perms"] and attrname != "coachmodified":
			job["coachmodified"] = True

		# Strip names before they can be used
		if attrname == "name": 
			job["name"] = str(value).strip().rstrip()

		# Make sure material can be used
		elif attrname == "material" and value in config["materials"]: 
			job["material"] = value

		#
		elif attrname == "esttime":
			# Cap the length using the configurable bounds
			bounds = config["length_bounds"]
			if bounds[0] >= 0:
				value = max(bounds[0], value)
			if bounds[1] >= 0:
				value = min(bounds[1], value)
			# Get the previous time, then set the new estimated time
			prevtime = job["esttime"]
			job["esttime"] = value
			# If priority is recalculated with time and you're not auth, recalc priority
			if config["recalc_priority"] and not authstate:
				newpriority = priority*1 # Make sure editing priority doesn't change newpriority
				job["totaldiff"] += value-prevtime # Add the difference between the times to the job's total difference.
				job["totaldiff"] = max(job["totaldiff"], 0) # Make sure total difference doesn't drop below 0.

				highestremoved = 0
				for i in config["priority_thresh"]: # A modified version of _calcpriority, to take out from the totaldiff.
					if job["totaldiff"] >= i and i < value:
						newpriority -= 1 # Lower priority for each thresh it passes.
						highestremoved = max(highestremoved, i)
				job["totaldiff"] -= highestremoved # Remove the thresh from the total difference.
				newpriority = max(newpriority, 0) # Keep the priority above 0.

				# If the new priority changed, remove and reinsert the job.
				if priority != newpriority:
					job["priority"] = newpriority 
					self.queue[priority].pop(index)
					self.queue[newpriority].append(job)

			elif authstate and config["recalc_priority"]: # If auth was needed to bypass the recalc, then add the gear.
				job["coachmodified"] = True

		elif attrname == "coachmodified": # Change the gear.
			job["coachmodified"] = bool(value)

		if argvs.loud: # if -v, report success
			newval = job[attrname]
			color = bcolors.MAGENTA if authstate else ""
			cprint("Changed {}'s `{}` value from {} to {}.\n({})".format(
				job["name"], attrname, oldval, newval, job["uuid"]), color=color)

