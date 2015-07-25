import json, os

from parseargv import args as argvs
from config import *
config = Config(CONFIGDIR)

def _comparetypes(obj, expected):
	"""
	Compare types, allowing exceptions.
	"""
	if expected is any_type:
		return True
	elif expected is any_number:
		if type(obj) is int or type(obj) is float:
			return True
	return type(obj) is expected

# Type exceptions
class any_type: pass 
class any_number: pass 

def runSocketCommand(commandlist, ws, socks, sessions, jdata, queue):
	"""
	Run a command based on `jdata`, from `commandlist`.
	"""
	if "action" not in jdata: 
		return "Action missing!"

	# Get the objects needed to run commands
	action = jdata["action"]
	sec = getsec(ws)
	args = dict(jdata)
	del args["action"]
	authstate = sessions.check(sec)

	# Stop actions that need auth if the client isn't auth
	if action in config["authactions"] and not authstate: 
		serveToConnection({"action":"deauthed"}, ws)
		return "This action requires auth."

	# Get a command dictionary for fast lookup
	cmds = {str(i): i for i in commandlist}

	# If the command can be run, run it
	if action in cmds and (not cmds[action].args or args):
		return cmds[action].run(args=args, authstate=authstate, sec=sec, sessions=sessions, ws=ws, sockets=socks, queue=queue)
	# If the action being bad is the problem, return that
	elif action not in cmds: 
		return "Bad command name."
	# If the args missing is the problem, return that
	elif not args:
		return "Args missing!"

class SocketCommand:
	"""
	A class used to define a socket command usable by `runSocketCommand`.
	"""
	def __init__(self, actionname, method, arglist):
		self.name = actionname
		self.method = method
		self.args = arglist
	def __str__(self):
		return self.name
	def run(self, **kwargs):
		args = kwargs["args"]
		# Check that each argument is correct
		for i in self.args:
			if i not in args:
				return "Expected '{}' argument, but didn't find it.".format(i)
			if not _comparetypes(args[i], self.args[i]):
				return "Expected '{}' argument to be an instance of '{}', but found an instance of '{}'.".format(
					i, self.args[i].__name__, type(args[i]).__name__)
		# Run the command if all is in order
		return self.method(**kwargs)

# Non-queue functions
def deauth(**kwargs): 
	"""
	Deauth the client.
	"""
	sec, sessions, ws = kwargs["sec"], kwargs["sessions"], kwargs["ws"]
	sessions.deauth(sec)
	serveToConnection({"action":"deauthed"}, ws)

	# If the verbose flag is used, print report
	if argvs.loud:
		cprint("Client successfully deauthed.")

def refresh(**kwargs): 
	"""
	Refresh all clients. (if the config allows it)
	"""
	socks, authstate = kwargs["sockets"], kwargs["authstate"]
	if config["allow_force_refresh"]:
		serveToConnections({"action":"refresh"}, socks)

		if argvs.loud: # If the verbose flag is used, print report
			color = bcolors.MAGENTA if authstate else ""
			cprint("Refreshed all clients.", color=color)
	else:
		cprint("Force refresh isn't enabled. (config.json, allow_force_refresh)", color=bcolors.YELLOW)

def uuddlrlrba(**kwargs):
	"""
	Huehuehue all clients. (if the config allows it)
	"""
	socks, authstate = kwargs["sockets"], kwargs["authstate"]
	if config["easter_eggs"]:
		serveToConnections({"action":"rickroll"}, socks)

		if argvs.loud: # If the verbose flag is used, print report
			color = bcolors.MAGENTA if authstate else bcolors.ENDC
			rainbow = "{}T{}r{}o{}l{}l{}e{}d{} all clients.".format(
				bcolors.RED, bcolors.ORANGE, bcolors.YELLOW, bcolors.GREEN, 
				bcolors.BLUE, bcolors.PURPLE, bcolors.DARKPURPLE, color) # RAINBOW \o/
			cprint(rainbow)
	else:
		cprint("This is a serious establishment, son. I'm dissapointed in you.", color=bcolors.YELLOW)

def auth(**kwargs):
	"""
	Attempt to auth the client using the `pass` argument.
	"""
	args, sec, sessions, ws = kwargs["args"], kwargs["sec"], kwargs["sessions"], kwargs["ws"]

	if config["admin_mode_enabled"]:
		if sessions.auth(sec, args["pass"]):
			serveToConnection({"action":"authed"}, ws)
			if argvs.loud: # If the verbose flag is used, print report
				cprint("Auth succeeded.", color=bcolors.MAGENTA)
		else:
			serveToConnection({"action":"authfailed"}, ws)
			if argvs.loud: # If the verbose flag is used, print report
				cprint("Auth failed.")

# Relative wrappers for queue actions
def append(**kwargs): kwargs["queue"].append(**kwargs)
def passoff(**kwargs): kwargs["queue"].passoff(**kwargs)
def remove(**kwargs): kwargs["queue"].remove(**kwargs)
def move(**kwargs): kwargs["queue"].move(**kwargs)
def relmove(**kwargs): kwargs["queue"].relmove(**kwargs)
def increment(**kwargs): kwargs["queue"].increment(**kwargs)
def decrement(**kwargs): kwargs["queue"].decrement(**kwargs)
def attr(**kwargs): kwargs["queue"].attr(**kwargs)

commands = [
	SocketCommand("deauth", deauth, {}),
	SocketCommand("refresh", refresh, {}),
	SocketCommand("uuddlrlrba", uuddlrlrba, {}),
	SocketCommand("auth", auth, {"pass": str}),
	SocketCommand("add", append, {"name": str, "priority": int, "time": any_number, "material": str}),
	SocketCommand("pass", passoff, {"uuid": str}),
	SocketCommand("remove", remove, {"uuid": str}),
	SocketCommand("move", move, {"uuid": str, "target_priority": int, "target_index": int}),
	SocketCommand("relmove", relmove, {"uuid": str, "target_index": int}),
	SocketCommand("increment", increment, {"uuid": str}),
	SocketCommand("decrement", decrement, {"uuid": str}),
	SocketCommand("attr", attr, {"uuid": str, "key": str, "new": any_type})
]

def buildCommands(plugins):
	"""
	Build the list of commands
	"""
	global commands
	for module in plugins:
		if hasattr(module, "socketCommands"):
			commands += module.socketCommands

def parseData(queue, ws, socks, sessions, jdata):
	"""
	Run the socket commands using the data given.
	"""
	global commands
	return runSocketCommand(commands, ws, socks, sessions, jdata, queue)

def generateData(queue):
	"""
	Generate data for sending to clients.
	"""
	jdata = {"action": "display"}
	jdata["queue"] = queue
	return jdata
