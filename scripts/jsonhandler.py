from parseargv import args as argvs
from util import *
from laserqueue import trigger_egg
config = Config(CONFIGDIR)

def _comparetypes(obj, expected):
	"""
	Compare types, allowing exceptions.
	"""
	global exceptions
	for exception in exceptions:
		if expected == exception:
			return exceptions[exception](obj)
	return type(obj) is expected

# Type exceptions
class any_type: pass
class any_number: pass
exceptions = {
	any_type:   lambda obj: True,
	any_number: lambda obj: isinstance(obj, int) or isinstance(obj, float)
}

authactions = config["authactions"]

def run_socket_command(commandlist, ws, socks, sessions, jdata, queue, printer):
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
		return cmds[action].run(args=args, authstate=authstate, sec=sec, sessions=sessions, ws=ws, sockets=socks, queue=queue, printer=printer)
	# If the action being bad is the problem, return that
	elif action not in cmds:
		return "Bad command name."
	# If the args missing is the problem, return that
	elif not args:
		return "Args missing!"

class SocketCommand:
	"""
	A class used to define a socket command usable by `run_socket_command`.
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
				if isinstance(self.args[i], list):
					args[i] = None
				else:
					return format("Expected '{nameofarg}' argument, but didn't find it.", nameofarg=i)
			if not _comparetypes(args[i], self.args[i]):
				if isinstance(self.args[i], list):
					args[i] = None
				else:
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
	sec, sessions, ws, printer = kwargs["sec"], kwargs["sessions"], kwargs["ws"], kwargs["printer"]
	sessions.deauth(sec)
	serve_connection({"action":"deauthed"}, ws)

	# If the verbose flag is used, print report
	if argvs.loud:
		printer.color_print("Client successfully deauthed.")

def refresh(**kwargs):
	"""
	Refresh all clients. (if the config allows it)
	"""
	socks, authstate, printer = kwargs["sockets"], kwargs["authstate"], kwargs["printer"]
	if config["allowForceRefresh"]:
		serve_connections({"action":"refresh"}, socks)

		if argvs.loud: # If the verbose flag is used, print report
			color = ansi_colors.MAGENTA if authstate else ""
			printer.color_print("Refreshed all clients.", color=color)
	else:
		printer.color_print("Force refresh isn't enabled. (config.json, allow_force_refresh)", color=ansi_colors.YELLOW)

def start_tour(**kwargs):
	"""
	Start the tour. (if the config allows it)
	"""
	socks, authstate, printer = kwargs["sockets"], kwargs["authstate"], kwargs["printer"]
	if config["allowTour"]:
		serve_connections({"action":"start_tour"}, socks)

		if argvs.loud: # If the verbose flag is used, print report
			color = ansi_colors.MAGENTA if authstate else ""
			printer.color_print("Started the tour.", color=color)
	else:
		printer.color_print("The tour isn't enabled. (config.json, allow_tour)", color=ansi_colors.YELLOW)

def auth(**kwargs):
	"""
	Attempt to auth the client using the `pass` argument.
	"""
	args, sec, sessions, ws, printer = kwargs["args"], kwargs["sec"], kwargs["sessions"], kwargs["ws"], kwargs["printer"]

	if config["adminModeEnabled"]:
		if sessions.auth(sec, args["pass"]):
			serve_connection({"action":"authed"}, ws)
			if argvs.loud: # If the verbose flag is used, print report
				printer.color_print("Auth succeeded.", color=ansi_colors.MAGENTA)
		else:
			serve_connection({"action":"auth_failed"}, ws)
			if argvs.loud: # If the verbose flag is used, print report
				printer.color_print("Auth failed.")

def egg(**kwargs):
	"""
	Attempt to trigger an easter egg.
	"""
	args, socks, ws, authstate, printer = kwargs["args"], kwargs["sockets"], kwargs["ws"], kwargs["authstate"], kwargs["printer"]
	if config["easterEggs"]:
		trigger_egg(args["trigger"], socks, ws, authstate, printer)
	else:
		printer.color_print("This code has a humor level of -1.")


# Relative wrappers for queue actions
append = lambda **kwargs: kwargs["queue"].append(**kwargs)
passoff = lambda **kwargs: kwargs["queue"].passoff(**kwargs)
remove = lambda **kwargs: kwargs["queue"].remove(**kwargs)
move = lambda **kwargs: kwargs["queue"].move(**kwargs)
relative_move = lambda **kwargs: kwargs["queue"].relative_move(**kwargs)
increment = lambda **kwargs: kwargs["queue"].increment(**kwargs)
decrement = lambda **kwargs: kwargs["queue"].decrement(**kwargs)
attr = lambda **kwargs: kwargs["queue"].attr(**kwargs)

commands = [
	SocketCommand("deauth", deauth, {}),
	SocketCommand("refresh", refresh, {}),
	SocketCommand("start_tour", start_tour, {}),
	SocketCommand("auth", auth, {"pass": str}),
	SocketCommand("egg", egg, {"trigger": str, "override": [bool]}),
	SocketCommand("add", append, {"name": str, "priority": int, "time": any_number, "material": str}),
	SocketCommand("pass", passoff, {"uuid": str}),
	SocketCommand("remove", remove, {"uuid": str}),
	SocketCommand("move", move, {"uuid": str, "target_priority": int, "target_index": int}),
	SocketCommand("relative_move", relative_move, {"uuid": str, "target_index": int}),
	SocketCommand("increment", increment, {"uuid": str}),
	SocketCommand("decrement", decrement, {"uuid": str}),
	SocketCommand("attr", attr, {"uuid": str, "key": str, "new": any_type})
]

def buildCommands(reg):
	"""
	Build the list of commands.
	"""
	global commands, authactions, exceptions
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

		toremove = []
		for oldcmd in commands:
			if str(oldcmd) == cmd[0]:
				toremove.append(oldcmd)
		for oldcmd in toremove:
			commands.remove(oldcmd)

		commands.append(SocketCommand(cmd[0], cmd[1], cmdargs))

	typelist = reg.events.get('socketType', {})
	types = [(i,typelist[i]) for i in typelist]
	for typeid, t in cmds:
		if len(t) != 2:
			continue
		if not isinstance(t[0], type):
			continue
		if not hasattr(t[1], "__call__"):
			continue

		exceptions[t[0]] = t[1]

	requireslist = reg.events.get('requiresAuth', {})
	requires = [(i,requireslist[i]) for i in requireslist]
	for _, required in requires:
		if not required:
			continue
		if not isinstance(required[0], str):
			continue
		authactions.append(required[0])

def parse_data(queue, ws, socks, sessions, jdata, printer):
	"""
	Run the socket commands using the data given.
	"""
	global commands
	return run_socket_command(commands, ws, socks, sessions, jdata, queue, printer)

def generate_data(queue):
	"""
	Generate data for sending to clients.
	"""
	jdata = {"action": "display"}
	jdata["queue"] = queue
	return jdata
