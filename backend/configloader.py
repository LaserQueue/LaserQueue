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

class WalkingConfig(Config):
	def __init__(self, path):
		filename = os.path.basename(path)
		findpath = os.path.dirname(path)
		self.path = None
		while True:
			if filename in os.listdir(findpath):
				self.path = os.path.join(findpath, filename)
				break
			elif os.path.abspath(findpath) == os.path.sep:
				raise FileNotFoundError(filename+" not found in directory tree.")
			findpath = os.path.join(findpath, "..")
		self.lastmodtime = os.path.getctime(self.path)
		self.data = json.load(open(self.path))


config = Config(os.path.join("..","www","config.json"))