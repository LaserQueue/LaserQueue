import json, os

config = json.load(open(os.path.join("..", "www", "config.json")))

def _typelist(l):
	return [type(i) for i in l]

def _comparetypes(args, expected):
	args = _typelist(args)
	args = [(int if i == float else i) for i in args]
	return args == expected


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

def parseData(queue, jdata):
	if jdata["action"] == "uuddlrlrba":
		return "uuddlrlrba"
	if "args" not in jdata or jdata["action"] == "null":
		return
	args = jdata["args"]

	if jdata["action"] == "move":
		if len(args) != 4:
			return "Expected 4 arguments, recieved "+str(len(args))
		expectedtypes = [int, int, int, int]
		if _typelist(args) != expectedtypes:
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.move(args[0],args[1],args[2],args[3])

	elif jdata["action"] == "smove":
		if len(args) != 3:
			return "Expected 3 arguments, recieved "+str(len(args))
		expectedtypes = [int, int, int]
		if _typelist(args) != expectedtypes:
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.smove(args[0],args[1],args[2])

	elif jdata["action"] == "remove":
		if len(args) != 2:
			return "Expected 2 arguments, recieved "+str(len(args))
		expectedtypes = [int, int]
		if _typelist(args) != expectedtypes:
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.remove(args[0],args[1])

	elif jdata["action"] == "sremove":
		if len(args) != 1:
			return "Expected 1 argument, recieved "+str(len(args))
		expectedtypes = [int]
		if _typelist(args) != expectedtypes:
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.sremove(args[0])

	elif jdata["action"] == "pass":
		if len(args) not in [1, 2]:
			return "Expected at most 2 arguments, recieved "+str(len(args))
		expectedtypes = [[int], [int, int]]
		if _typelist(args) not in expectedtypes:
			return "Expected "+str(expectedtypes[0])+" or "+str(expectedtypes[1])+", recieved "+str(_typelist(args))

		queue.passoff(args[0], args[1] if len(args)>1 else 0)

	elif jdata["action"] == "spass":
		if len(args) != 1:
			return "Expected 1 argument, recieved "+str(len(args))
		expectedtypes = [int]
		if _typelist(args) != expectedtypes:
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.spass(args[0])

	elif jdata["action"] == "add":
		if len(args) != 4:
			return "Expected 4 arguments, recieved "+str(len(args))
		expectedtypes = [str, int, int, str]
		if not _comparetypes(args, expectedtypes):
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.append(args[0],args[1],args[2],args[3])
	elif jdata["action"] == "sdecrement":
		if len(args) != 1:
			return "Expected 1 argument, recieved "+str(len(args))
		expectedtypes = [int]
		if _typelist(args) != expectedtypes:
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.sdecrement(args[0])
	elif jdata["action"] == "sincrement":
		if len(args) != 1:
			return "Expected 1 argument, recieved "+str(len(args))
		expectedtypes = [int]
		if _typelist(args) != expectedtypes:
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.sincrement(args[0])


	elif jdata["action"] == "upass":
		if len(args) != 1:
			return "Expected 1 argument, recieved "+str(len(args))
		expectedtypes = [str]
		if _typelist(args) != expectedtypes:
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.upass(args[0])
	elif jdata["action"] == "uremove":
		if len(args) != 1:
			return "Expected 1 argument, recieved "+str(len(args))
		expectedtypes = [str]
		if _typelist(args) != expectedtypes:
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.uremove(args[0])
	elif jdata["action"] == "umove":
		if len(args) != 3:
			return "Expected 3 arguments, recieved "+str(len(args))
		expectedtypes = [str, int, int]
		if _typelist(args) != expectedtypes:
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.umove(args[0], args[1], args[2])
	elif jdata["action"] == "uincrement":
		if len(args) != 1:
			return "Expected 1 argument, recieved "+str(len(args))
		expectedtypes = [str]
		if _typelist(args) != expectedtypes:
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.uincrement(args[0])
	elif jdata["action"] == "udecrement":
		if len(args) != 1:
			return "Expected 1 argument, recieved "+str(len(args))
		expectedtypes = [str]
		if _typelist(args) != expectedtypes:
			return "Expected "+str(expectedtypes)+", recieved "+str(_typelist(args))

		queue.udecrement(args[0])

	# auth packet	
	elif jdata["action"] == "auth":
		if len(args) != 1:
			return "Expected 1 argument, recieved "+str(len(args))
		if type(args[0]) != str:
			return "The password must be a string."
		if os.path.exists("password") and not config["admin_mode_enabled"]:
			password = open("password").read().strip().rstrip()
			if args[0].strip().rstrip() == password:
				return "auth successful"
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

def generateData(queue, esttime, currtime):
	jdata = {}
	jdata["queue"] = queue.queue
	jdata["esttime"] = esttime
	jdata["currtime"] = currtime
	jdata["action"] = "display"
	return json.dumps(jdata)










