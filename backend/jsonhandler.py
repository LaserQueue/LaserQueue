import json, os

from configloader import config

def _typelist(l):
	return [type(i) for i in l]

def _comparetypes(args, expected, numbers = False):
	args = _typelist(args)
	if numbers: args = [(int if i == float else i) for i in args]
	exp = expected[:]
	for ii in range(len(exp)):
		i = exp[ii]
		if i is any_type:
			exp[ii] = args[ii]
	return args == exp


class any_type: pass # typelist exception

"""
Format for site-to-program data:
{
	"action": "type of action to perform",
	"args": [the data the function requires]
}


possible actions:
move (args original index, target index, original priority, target priority)
remove (args index, priority)
pass (args priority, optional arg index with default 0)
add (args name, base priority, estimated time in minutes, material code)


exceptions: if move target index is -1, it will append to the bottom of the list
"""

def parseData(queue, sessions, jdata, shamed):
	if "sid" in jdata and "action" in jdata:
		sid = jdata["sid"]
		action = jdata["action"]
		authstate = sessions.check(sid)
		if action in config["authactions"] and not authstate: return
		if action == "uuddlrlrba":
			return "uuddlrlrba"
		elif action == "deauth":
			sessions.deauth(sid)
			return
		elif action == "null":
			sessions.newnull(sid)
			sessions.update()
			return
		elif action == "shame":
			return "sorry"
		elif action == "refresh":
			return "refresh"
	else:
		return
	if "args" not in jdata:
		return

	args = jdata["args"]

	if action == "auth" and config["admin_mode_enabled"]:
		if len(args) != 1:
			return "Expected 1 argument, received "+str(len(args))
		expectedtypes = [str]
		if not _comparetypes(args, expectedtypes):
			return "Expected "+str(expectedtypes)+", received "+str(_typelist(args))

		return sessions.auth(sid, args[0])

	elif action == "add":
		if len(args) != 4:
			return "Expected 4 arguments, received "+str(len(args))
		expectedtypes = [str, int, int, str]
		if not _comparetypes(args, expectedtypes, numbers=True):
			return "Expected "+str(expectedtypes)+", received "+str(_typelist(args))

		queue.append(args[0],args[1],args[2],args[3], sid, authstate)

	elif action == "pass":
		if len(args) != 1:
			return "Expected 1 argument, received "+str(len(args))
		expectedtypes = [str]
		if not _comparetypes(args, expectedtypes):
			return "Expected "+str(expectedtypes)+", received "+str(_typelist(args))

		queue.passoff(args[0])
	elif action == "remove":
		if len(args) != 1:
			return "Expected 1 argument, received "+str(len(args))
		expectedtypes = [str]
		if not _comparetypes(args, expectedtypes):
			return "Expected "+str(expectedtypes)+", received "+str(_typelist(args))

		queue.remove(args[0])
	elif action == "move":
		if len(args) != 3:
			return "Expected 3 arguments, received "+str(len(args))
		expectedtypes = [str, int, int]
		if not _comparetypes(args, expectedtypes):
			return "Expected "+str(expectedtypes)+", received "+str(_typelist(args))

		queue.move(args[0], args[1], args[2])
	elif action == "increment":
		if len(args) != 1:
			return "Expected 1 argument, received "+str(len(args))
		expectedtypes = [str]
		if not _comparetypes(args, expectedtypes):
			return "Expected "+str(expectedtypes)+", received "+str(_typelist(args))

		queue.increment(args[0])
	elif action == "decrement":
		if len(args) != 1:
			return "Expected 1 argument, received "+str(len(args))
		expectedtypes = [str]
		if not _comparetypes(args, expectedtypes):
			return "Expected "+str(expectedtypes)+", received "+str(_typelist(args))

		queue.decrement(args[0])
	elif action == "attr":
		if len(args) != 3:
			return "Expected 3 arguments, received "+str(len(args))
		expectedtypes = [str, str, any_type]
		if not _comparetypes(args, expectedtypes):
			return "Expected "+str(expectedtypes)+", received "+str(_typelist(args))

		queue.attr(args[0],args[1],args[2],authstate)


	else:
		return "Bad action name"


"""
Format for program-to-site data:
{
	"queue": [
	[
		{
			"name": "student's name",
			"material": "material code"
		}
	],  // Priority 0
	[], // Priority 1
	[], // ...
	[], // ...
	[], // ...
	[]  // Priority 5 (highest priority)
	],
	"esttime": estimated time of cut in seconds,
	"currtime": amount of time the laser has been cutting
}
"""

def generateData(queue, sessions, shamed):
	jdata = {}
	jdata["queue"] = queue.queue
	jdata["action"] = "display"
	jdata["auths"] = sessions.cutauths()
	jdata["deauths"] = shamed
	return jdata










