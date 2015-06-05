import os, json

class Config:
	def __init__(self, path):
		self.path = path
		self.lastmodtime = os.path.getctime(path)
		self.data = json.load(open(path))
	def __getitem__(self, y):
		if os.path.getctime(self.path) > self.lastmodtime:
			self.data = json.load(self.path)
			lastmodtime = os.path.getctime(self.path)
		return self.data[y]

config = Config(os.path.join("..","www","config.json"))