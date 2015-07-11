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
import hashlib

from config import *
config = Config(os.path.join("..","www","config.json"))

if os.path.exists("password"):
	opass = open("password").read().strip().rstrip()
	hash_object = hashlib.sha1(opass.encode()).hexdigest()
	hashed_final = hashlib.sha1(hash_object.encode()).hexdigest()
	hashed = open("hashpassword", "w")
	hashed.write(hashed_final)
	hashed.close()
	os.remove("password")
if os.path.exists("hashpassword"):
	PASSWORD = open("hashpassword").read().strip().rstrip()

class SID:
	def __init__(self, seckey=None):
		self.lasttimestamp = time.time()
		self.timestamp = time.time()
		self.authstamp = time.time()
		self.authstate = False
		self.seckey = str(seckey)
	@classmethod
	def load(cls, jdata):
		self = cls()
		self.lasttimestamp = jdata["laststamp"]
		self.timestamp = jdata["stamp"]
		self.authstamp = jdata["authstamp"]
		self.authstate = jdata["auth"]
		self.seckey = str(jdata.get("seckey"))
		return self
	def serialize(self):
		return {
			"stamp": self.timestamp,
			"laststamp": self.lasttimestamp,
			"authstamp": self.authstamp,
			"auth": self.authstate,
			"seckey": self.seckey
		}
	def auth(self, password):
		if os.path.exists("hashpassword"):
			hash_object = hashlib.sha1(password.strip().rstrip().encode()).hexdigest()
			if hash_object.strip().rstrip() == PASSWORD: 
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
	@classmethod
	def load(cls, jdata):
		self = cls()
		for sid in jdata:
			self.sids.append(SID.load(sid))
		return self
	def check(self, sec):
		csid = self._get(sec)
		if not csid:               return False
		elif not csid.checkstate(): 
			self.sids.remove(csid);  return False
		csid.onupdate()
		if not csid.authstate:     return False
		return True
	def auth(self, sec, password):
		if self.check(sec) or self._get(sec).auth(password): 
			return True
		return False
	def deauth(self, sec):
		self._get(sec).deauth()
	def serialize(self):
		return [sid.serialize() for sid in self.sids]
	def allauth(self):
		return [sid.seckey for sid in self.sids if sid.authstate]
	def allnonauth(self):
		return [sid.seckey for sid in self.sids if not sid.authstate]
	def _isin(self, sec):
		for i in self.sids:
			if i.seckey == sec:
				return True
		return False
	def _get(self, sec):
		if not self._isin(sec):
			self.sids.append(SID(sec))
		for sid in self.sids:
			if sid.seckey == sec:
				return sid
	def update(self):
		for sid in self.sids:
			self.check(sid.seckey)

