import json, os

from config import *
config = Config(os.path.join("..","www","config.json"))

def _typelist(l):
	return [type(i) for i in l]

def _comparetypes(obj, expected):
	if expected is any_type:
		return True
	elif expected is any_number:
		if type(obj) is int or type(obj) is float:
			return True
	return type(obj) is expected

# typelist exceptions
class any_type: pass 
class any_number: pass 

def runSocketCommand(commandlist, ws, socks, sessions, jdata):
	if "action" not in jdata: 
		return "Action missing!"

	action = jdata["action"]
	sec = getsec(ws)
	args = dict(jdata)
	del args["action"]
	authstate = sessions.check(sec)

	if action in config["authactions"] and not authstate: 
		return "This action requires auth."

	cmds = {str(i): i for i in commandlist}

	if action in cmds and (not cmds[action].args or args):
		return cmds[action].run(args=args, authstate=authstate, sec=sec, sessions=sessions, ws=ws, sockets=socks)
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
		args = kwargs["args"]
		for i in self.args:
			if i not in args:
				return "Expected '{}' argument, but didn't find it.".format(i)
			if not _comparetypes(args[i], self.args[i]):
				return "Expected '{}' argument to be an instance of '{}', but found an instance of '{}'.".format(
					i, self.args[i].__name__, type(args[i]).__name__)
		return self.method(**kwargs)

# Non-queue functions
def deauth(**kwargs): 
	sec, sessions, ws = kwargs["sec"], kwargs["sessions"], kwargs["ws"]
	sessions.deauth(sec)
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
	args, sec, sessions, ws = kwargs["args"], kwargs["sec"], kwargs["sessions"], kwargs["ws"]
	sec = getsec(ws)
	if config["admin_mode_enabled"]:
		if sessions.auth(sec, args["pass"]):
			serveToConnection({"action":"authed"}, ws)
		else:
			serveToConnection({"action":"authfailed"}, ws)

def parseData(queue, ws, socks, sessions, jdata):
	commands = [
		SocketCommand("deauth", deauth, {}),
		SocketCommand("refresh", refresh, {}),
		SocketCommand("uuddlrlrba", uuddlrlrba, {}),
		SocketCommand("auth", auth, {"pass": str}),
		SocketCommand("add", queue.append, {"name": str, "priority": int, "time": any_number, "material": str}),
		SocketCommand("pass", queue.passoff, {"uuid": str}),
		SocketCommand("remove", queue.remove, {"uuid": str}),
		SocketCommand("move", queue.move, {"uuid": str, "target_priority": int, "target_index": int}),
		SocketCommand("relmove", queue.relmove, {"uuid": str, "target_index": int}),
		SocketCommand("increment", queue.increment, {"uuid": str}),
		SocketCommand("decrement", queue.decrement, {"uuid": str}),
		SocketCommand("attr", queue.attr, {"uuid": str, "key": str, "new": any_type})
	]
	return runSocketCommand(commands, ws, socks, sessions, jdata)

def generateData(queue):
	jdata = {"action": "display"}
	jdata["queue"] = queue
	return jdata
