# sid handler. it will hold sids (and cache them with -b), and return their validity.


# SID logic:
# 	if sid doesn't exist:
# 		return False on auth, add sid to list with timestamp of connection; lasttimestamp is now
# 	if sid exists and is not authorized:
# 		return False on auth, set lasttimestamp to now
# 	if sid exists and is over 60 minutes old:
# 		destroy, return False
# 	if sid exists and has gone 20 minutes since lasttimestamp:
# 		destroy, return False

import time
import json
import os

config = json.load(open(os.path.join("..", "www", "config.json")))

class SID:
	def __init__(self, uuid):
		self.lasttimestamp = time.time()
		self.timestamp = time.time()
		self.authstamp = time.time()
		self.authstate = False
		self.uuid = uuid
	def load(jdata): #initialization method, do not call on existing object
		self = SID(None)
		self.lasttimestamp = jdata["laststamp"]
		self.timestamp = jdata["stamp"]
		self.authstamp = jdata["authstamp"]
		self.authstate = jdata["auth"]
		self.uuid = jdata["uuid"]
		return self
	def serialize(self):
		return {
			"stamp": self.timestamp,
			"laststamp": self.lasttimestamp,
			"authstamp": self.authstamp,
			"auth": self.authstate,
			"uuid": self.uuid
		}
	def auth(self, password):
		if os.path.exists("password"):
			correctpass = open("password").read().strip().rstrip()
			if password.strip().rstrip() == correctpass: # *sighs* I'll hash-salt the password one of these days.
				self.authstate = True
				return True
		return False
	def deauth(self):
		self.authstate = False
	def checkstate(self):
		timestamp = time.time()
		if timestamp-self.authstamp > config["auth_timeout"] and config["auth_timeout"]:
			self.authstate = False
		if timestamp-self.lasttimestamp > config["lastuse_timeout"] and config["lastuse_timeout"]:
			return False
		elif timestamp-self.timestamp > config["sid_total_timeout"] and config["sid_total_timeout"]:
			return False
		return True
	def onupdate(self):
		self.lasttimestamp = time.time()
		self.authstamp = time.time()
	def regen(self):
		self.lasttimestamp = time.time()
		self.timestamp = time.time()
		self.authstamp = time.time()
		self.authstate = False


class SIDCache:
	def __init__(self):
		self.sids = []
	def load(jdata): #initialization method, do not call on existing object
		self = SIDCache()
		for sid in jdata:
			self.sids.append(SID.load(sid))
		return self
	def check(self, uuid):
		csid = self._get(uuid)
		if not csid:               return False
		elif not csid.checkstate(): 
			self.sids.remove(csid);  return False
		csid.onupdate()
		if not csid.authstate:     return False
		return True
	def auth(self, uuid, password):
		if self.check(uuid) or self._get(uuid).auth(password): 
			return True
		return False
	def deauth(self, uuid):
		self._get(uuid).deauth()
	def serialize(self):
		return [sid.serialize() for sid in self.sids]
	def allauth(self):
		return [sid.uuid for sid in self.sids if sid.authstate]
	def cutauths(self):
		return [sid.uuid[:len(sid.uuid)/2] for sid in self.sids if sid.authstate]
	def allnonauth(self):
		return [sid.uuid for sid in self.sids if not sid.authstate]
	def _isin(self, uuid):
		for i in self.sids:
			if i.uuid == uuid:
				return True
		return False
	def _get(self, uuid):
		if not self._isin(uuid):
			self.sids.append(SID(uuid))
		for sid in self.sids:
			if sid.uuid == uuid:
				return sid

def cache(sids):
	json.dump(sids.serialize(), open("scache.json", "w"), indent=2)

def loadcache():
	if os.path.exists("scache.json"):
		return SIDCache.load(json.load(open("scache.json")))
	else:
		return SIDCache()

