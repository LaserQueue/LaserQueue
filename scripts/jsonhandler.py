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
	if "args" in jdata:
		args = jdata["args"]
	else:
		args = None
	authstate = sessions.check(sid)

	if action in config["authactions"] and not authstate: 
		return "This action requires auth."

	cmds = {str(i): i for i in commandlist}

	if action in cmds and (not cmds[action].args or args):
		return cmds[action].run(args=args, authstate=authstate, sid=sid, sessions=sessions)
	elif not args: 
		return "Args missing!"
	else:
		return "Bad command name."

class SocketCommand:
	def __init__(self, actionname, method, arglist):
		self.name = actionname
		self.method = method
		self.args = arglist
	def __str__(self):
		return self.name
	def run(self, **kwargs):
		if self.args:
			args = kwargs["args"]
			if not args:
				return "Expected {} argument{}, received {}".format(len(self.args), 
					"s" if len(self.args) != 1 else "", 0)
			elif len(args) != len(self.args):
				return "Expected {} argument{}, received {}".format(len(self.args), 
					"s" if len(self.args) != 1 else "", len(args))
			elif not _comparetypes(args, self.args):
				return "Expected "+str(self.args)+", received "+str(_typelist(args))
		return self.method(**kwargs)


# Non-queue functions
def null(**kwargs): 
	sid, sessions = kwargs["sid"], kwargs["sessions"]
	sessions.newnull(sid)
	sessions.update()
def deauth(**kwargs): 
	sid, sessions = kwargs["sid"], kwargs["sessions"]
	sessions.deauth(kwargs["sid"])
def shame(**kwargs): return "sorry"
def refresh(**kwargs): return "refresh"
def uuddlrlrba(**kwargs): return "uuddlrlrba"
def auth(**kwargs):
	args, sid, sessions = kwargs["args"], kwargs["sid"], kwargs["sessions"]
	if config["admin_mode_enabled"]:
		if not sessions.auth(sid, args[0]):
			return "authfail"

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
	jdata["queue"] = queue
	jdata["action"] = "display"
	jdata["auths"] = sessions.cutauths()
	jdata["deauths"] = shamed
	return jdata










