import json, os

from config import *
config = Config(os.path.join("..","www","config.json"))

def _typelist(l):
	return [type(i) for i in l]

def _comparetypes(args, expected):
	args = _typelist(args)
	exp = expected[:]
	for ii in range(len(exp)):
		i = exp[ii]
		if i is any_type:
			exp[ii] = args[ii]
		elif i is any_number:
			if args[ii] in [int, float]:
				exp[ii] = args[ii]
	return args == exp

# typelist exceptions
class any_type: pass 
class any_number: pass 

def runSocketCommand(commandlist, jdata, sessions):
	if "action" not in jdata: 
		return "Action missing!"
	if "sid" not in jdata:
		return "Session ID missing!"

	action = jdata["action"]
	sid = jdata["sid"]
	authstate = sessions.check(sid)

	if action in config["authactions"] and not authstate: 
		return "This action requires auth."

	cmd_noargs = {str(i): i for i in commandlist if not i.args}
	cmd_args = {str(i): i for i in commandlist if i.args}

	if action in cmd_noargs:
		return cmd_noargs[action].run(None, authstate, sid, sessions)
	elif "args" not in jdata: 
		return "Args missing!"
	elif action in cmd_args:
		args = jdata["args"]
		return cmd_args[action].run(args, authstate, sid, sessions)
	else:
		return "Bad command name."

class SocketCommand:
	def __init__(self, actionname, method, arglist):
		self.name = actionname
		self.method = method
		self.args = arglist
	def __str__(self):
		return self.name
	def run(self, args, authstate, sid, sessions):
		if self.args:
			if len(args) != len(self.args):
				return "Expected "+str(len(self.args))+" argument, received "+str(len(args))
			if not _comparetypes(args, self.args):
				return "Expected "+str(self.args)+", received "+str(_typelist(args))
			return self.method(args, authstate, sid, sessions)
		else:
			return self.method(authstate, sid, sessions)


# Non-queue functions
def null(authstate, sid, sessions): sessions.newnull(sid); sessions.update()
def deauth(authstate, sid, sessions): sessions.deauth(sid)
def shame(authstate, sid, sessions): return "sorry"
def refresh(authstate, sid, sessions): return "refresh"
def uuddlrlrba(authstate, sid, sessions): return "uuddlrlrba"
def auth(args, authstate, sid, sessions):
	if config["admin_mode_enabled"]:
		return sessions.auth(sid, args[0])

def parseData(queue, sessions, jdata):
	commands = [
		SocketCommand("null", null, None),
		SocketCommand("deauth", deauth, None),
		SocketCommand("shame", shame, None),
		SocketCommand("refresh", refresh, None),
		SocketCommand("uuddlrlrba", uuddlrlrba, None),
		SocketCommand("auth", auth, [str]),
		SocketCommand("add", queue.append, [str, int, any_number, str]),
		SocketCommand("pass", queue.passoff, [str]),
		SocketCommand("remove", queue.remove, [str]),
		SocketCommand("move", queue.move, [str, int, int]),
		SocketCommand("relmove", queue.relmove, [str, int]),
		SocketCommand("increment", queue.increment, [str]),
		SocketCommand("decrement", queue.decrement, [str]),
		SocketCommand("attr", queue.attr, [str, str, any_type])
	]
	return runSocketCommand(commands, jdata, sessions)

def generateData(queue, sessions, shamed):
	jdata = {}
	jdata["queue"] = queue.queue
	jdata["action"] = "display"
	jdata["auths"] = sessions.cutauths()
	jdata["deauths"] = shamed
	return jdata










