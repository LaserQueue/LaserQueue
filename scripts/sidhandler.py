# sid handler. it will hold sids and return their validity.

import time
import json
import os
import hashlib

from util import *
config = Config(CONFIGDIR)

selfpath = os.path.dirname(__file__)

if os.path.exists(os.path.join(selfpath, "hashpassword")):
	PASSWORD = open(os.path.join(selfpath, "hashpassword")).read().strip()

class SID:
	"""
	A single session instance.
	"""
	def __init__(self, seckey=None):
		self.stamp = time.time()
		self.authstate = False
		self.seckey = str(seckey)

	def auth(self, password):
		"""
		Attempt to auth using `password`, by checking it against PASSWORD.
		"""
		if os.path.exists(os.path.join(selfpath, "hashpassword")):
			hash_object = hashlib.sha256(password.strip().encode()).hexdigest()
			if hash_object.strip() == PASSWORD:
				self.authstate = True
				return True
		return False

	def deauth(self):
		"""
		Remove this session's authstate.
		"""
		self.authstate = False

	def checkstate(self):
		"""
		Check this session's state, making sure that nothing has timed out yet.
		"""
		timestamp = time.time()
		if timestamp-self.stamp > config["authTimeout"] and config["authTimeout"]:
			self.deauth()

	def onupdate(self):
		"""
		Update the session's timestamps.
		"""
		self.stamp = time.time()



class SIDCache:
	"""
	A collection of session instances.
	"""
	def __init__(self):
		self.sids = []

	def check(self, sec):
		"""
		Get the authstate of the specified key, and regen if needed.
		"""
		csid = self._get(sec)
		if not csid:               return False # If the key doesn't exist, return False

		# update the SID
		csid.checkstate()
		csid.onupdate()

		if not csid.authstate:     return False # If the key isn't authed, return False
		return True # Otherwise, return True
	def auth(self, sec, password):
		"""
		Attempt to auth `sec` using `password`.
		"""
		if self.check(sec) or self._get(sec).auth(password):
			return True # If the key's already authed or the auth succeeded, return True
		return False

	def deauth(self, sec):
		"""
		Deauth `sec`.
		"""
		self._get(sec).deauth()

	def allauth(self):
		"""
		Return a list of every authed key.
		"""
		return [sid.seckey for sid in self.sids if sid.authstate]

	def _isin(self, sec):
		"""
		Check if the key is in the cache.
		"""
		for i in self.sids:
			if i.seckey == sec:
				return True
		return False

	def _get(self, sec):
		"""
		Get the session for the key given.
		"""
		if not self._isin(sec): # If it doesn't exist, make it
			self.sids.append(SID(sec))

		for sid in self.sids:
			if sid.seckey == sec:
				return sid
	def update(self):
		"""
		Iterate through every session and update it.
		"""
		for sid in self.sids:
			self.check(sid.seckey)
