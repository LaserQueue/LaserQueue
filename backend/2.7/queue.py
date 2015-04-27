import json

config = json.load(open("laserqueue.json"))

lpri = len(config["priority"])-1

def _calcpriority(priority, time):
	for i in config["priority_thresh"]:
		if time >= i:
			priority -= 1
	return max(priority, 0)

class Queue:
	def __init__(self):
		self.queue = [[] for i in config["priority"]]
	def append(self, name, priority, esttime, material):
		priority = _calcpriority(priority, esttime)

		inqueue = False
		for i in self.queue:
			for j in i: 
				if name.lower() == j["name"].lower() and material == j["material"]:
					inqueue = True
					break

		if not inqueue:
			self.queue[lpri-priority].append({
				"name": name,
				"material": material,
				"esttime": esttime,
				"coachmodified": False
			})

	def passoff(self, priority, index=0):
		if not priority and len(self.queue[lpri-priority]) < index:
			return
		item = self.queue[lpri-priority].pop(index)
		index += 1
		if len(self.queue[lpri-priority]) < index:
			priority -= 1
			index = 0
		self.queue[lpri-priority].insert(max(index, 0),item)
		
	def move(self, in1, in2, pr1, pr2):
		item = self.queue[lpri-pr1].pop(in1)
		item["coachmodified"] = True
		if in2 >= 0:
			self.queue[lpri-pr2].insert(in2, item)
		else:
			self.queue[lpri-pr2].append(item)
	def remove(self, priority, index):

		del self.queue[lpri-priority][index]
	def sremove(self, index):
		gi = 0
		for ii in xrange(len(self.queue)):
			if index+1 <= gi+len(self.queue[ii]):
				del self.queue[ii][index-gi]
				return
			gi += len(self.queue[ii])
	def spass(self, oindex):
		gi = 0
		for ii in xrange(len(self.queue)):
			if oindex+1 <= gi+len(self.queue[ii]):
				index = oindex-gi
				priority = lpri-ii
				break
			gi += len(self.queue[ii])


		if not priority and len(self.queue[lpri-priority]) < index:
			return
		item = self.queue[lpri-priority].pop(index)
		index += 1
		if len(self.queue[lpri-priority]) < index:
			priority -= 1
			index = 0
		self.queue[min(lpri-priority, 5)].insert(max(index, 0),item)

