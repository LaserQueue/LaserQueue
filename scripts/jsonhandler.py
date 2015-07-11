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

def runSocketCommand(commandlist, ws, socks, sessions, jdata):
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
	authstate = sessions.check(sid, getsec(ws))

	if action in config["authactions"] and not authstate: 
		return "This action requires auth."

	cmds = {str(i): i for i in commandlist}

	if action in cmds and (not cmds[action].args or args):
		return cmds[action].run(args=args, authstate=authstate, sid=sid, sessions=sessions, ws=ws, sockets=socks)
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
def deauth(**kwargs): 
	sid, sessions, ws = kwargs["sid"], kwargs["sessions"], kwargs["ws"]
	sec = getsec(ws)
	sessions.deauth(kwargs["sid"], sec)
	serveToConnection({"action":"deauthed"}, ws)
def refresh(**kwargs): 
	socks = kwargs["sockets"]
	if config["allow_force_refresh"]:
		serveToConnections({"action":"refresh"}, socks)
	else:
		cprint(bcolors.YELLOW + "Force refresh isn't enabled. (config.json, allow_force_refresh)")
def uuddlrlrba(**kwargs):
	socks = kwargs["sockets"]
	if config["easter_eggs"]:
		serveToAllConnections({"action":"rickroll"}, socks)
	else:
		cprint(bcolors.YELLOW + "This is a serious establishment, son. I'm dissapointed in you.")
def auth(**kwargs):
	args, sid, sessions, ws = kwargs["args"], kwargs["sid"], kwargs["sessions"], kwargs["ws"]
	sec = getsec(ws)
	if config["admin_mode_enabled"]:
		if sessions.auth(sid, sec, args[0]):
			serveToConnection({"action":"authed"}, ws)
		else:
			serveToConnection({"action":"authfailed"}, ws)

def parseData(queue, ws, socks, sessions, jdata):
	commands = [
		SocketCommand("deauth", deauth, None),
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
	return runSocketCommand(commands, ws, socks, sessions, jdata)

def generateData(queue):
	jdata = {"action": "display"}
	jdata["queue"] = queue
	return jdata
