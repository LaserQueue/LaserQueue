from parseargv import args as argvs
from util import *
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

authactions = config["authactions"]

def runSocketCommand(commandlist, ws, socks, sessions, jdata, queue):
	"""
	Run a command based on `jdata`, from `commandlist`.
	"""
	global authactions
	if "action" not in jdata: 
		return "Action missing!"

	# Get the objects needed to run commands
	action = jdata["action"]
	sec = get_sec_key(ws)
	args = dict(jdata)
	del args["action"]
	authstate = sessions.check(sec)

	# Stop actions that need auth if the client isn't auth
	if action in authactions and not authstate: 
		serve_connection({"action":"deauthed"}, ws)
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
				return format("Expected '{nameofarg}' argument, but didn't find it.", nameofarg=i)
			if not _comparetypes(args[i], self.args[i]):
				return format("Expected '{nameofarg}' argument to be an instance of '{typeexpected}', but found an instance of '{typeofarg}'.",
					nameofarg = i, 
					typeexpected = self.args[i].__name__, 
					typeofarg = type(args[i]).__name__)
		# Run the command if all is in order
		return self.method(**kwargs)

# Non-queue functions
def deauth(**kwargs): 
	"""
	Deauth the client.
	"""
	sec, sessions, ws = kwargs["sec"], kwargs["sessions"], kwargs["ws"]
	sessions.deauth(sec)
	serve_connection({"action":"deauthed"}, ws)

	# If the verbose flag is used, print report
	if argvs.loud:
		color_print("Client successfully deauthed.")

def refresh(**kwargs): 
	"""
	Refresh all clients. (if the config allows it)
	"""
	socks, authstate = kwargs["sockets"], kwargs["authstate"]
	if config["allow_force_refresh"]:
		serve_connections({"action":"refresh"}, socks)

		if argvs.loud: # If the verbose flag is used, print report
			color = ansi_colors.MAGENTA if authstate else ""
			color_print("Refreshed all clients.", color=color)
	else:
		color_print("Force refresh isn't enabled. (config.json, allow_force_refresh)", color=ansi_colors.YELLOW)

def starttour(**kwargs): 
	"""
	Start the tour. (if the config allows it)
	"""
	socks, authstate = kwargs["sockets"], kwargs["authstate"]
	if config["allow_tour"]:
		serve_connections({"action":"starttour"}, socks)

		if argvs.loud: # If the verbose flag is used, print report
			color = ansi_colors.MAGENTA if authstate else ""
			color_print("Started the tour.", color=color)
	else:
		color_print("The tour isn't enabled. (config.json, allow_tour)", color=ansi_colors.YELLOW)

def auth(**kwargs):
	"""
	Attempt to auth the client using the `pass` argument.
	"""
	args, sec, sessions, ws = kwargs["args"], kwargs["sec"], kwargs["sessions"], kwargs["ws"]

	if config["admin_mode_enabled"]:
		if sessions.auth(sec, args["pass"]):
			serve_connection({"action":"authed"}, ws)
			if argvs.loud: # If the verbose flag is used, print report
				color_print("Auth succeeded.", color=ansi_colors.MAGENTA)
		else:
			serve_connection({"action":"authfailed"}, ws)
			if argvs.loud: # If the verbose flag is used, print report
				color_print("Auth failed.")


# Relative wrappers for queue actions
append = lambda **kwargs: kwargs["queue"].append(**kwargs)
passoff = lambda **kwargs: kwargs["queue"].passoff(**kwargs)
remove = lambda **kwargs: kwargs["queue"].remove(**kwargs)
move = lambda **kwargs: kwargs["queue"].move(**kwargs)
relmove = lambda **kwargs: kwargs["queue"].relmove(**kwargs)
increment = lambda **kwargs: kwargs["queue"].increment(**kwargs)
decrement = lambda **kwargs: kwargs["queue"].decrement(**kwargs)
attr = lambda **kwargs: kwargs["queue"].attr(**kwargs)

commands = [
	SocketCommand("deauth", deauth, {}),
	SocketCommand("refresh", refresh, {}),
	SocketCommand("starttour", starttour, {}),
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

def buildCommands(plugins, reg):
	"""
	Build the list of commands.
	"""
	global commands, authactions
	commandlist = reg.events.get('socket', {})
	cmds = [(i,commandlist[i]) for i in commandlist]
	for cmdid, cmd in cmds:
		if not (2 <= len(cmd) <= 3): 
			continue
		if not isinstance(cmd[0], str) or not cmd[0]:
			continue
		if not hasattr(cmd[1], "__call__"):
			continue
		if len(cmd) > 2 and not isinstance(cmd[2], dict):
			continue

		if len(cmd) <= 2:
			cmdargs = {}
		else:
			cmdargs = cmd[2]
		commands.append(SocketCommand(cmd[0], cmd[1], cmdargs))
	for module in plugins:
		if hasattr(module, "requiresAuth"):
			authactions += module.requiresAuth

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
