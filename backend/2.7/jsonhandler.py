import json
# add other part imports at future point

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
	if "args" not in jdata:
		return
	if jdata["action"] == "null":
		return
	args = jdata["args"]
	if jdata["action"] == "move":
		if len(jdata["args"]) != 4:
			print "Expected 4 arguments, recieved "+len(jdata["args"])
			return

		queue.move(args[0],args[1],args[2],args[3])

	elif jdata["action"] == "remove":
		if len(jdata["args"]) != 2:
			print "Expected 2 arguments, recieved "+len(jdata["args"])
			return

		queue.remove(args[0],args[1])

	elif jdata["action"] == "sremove":
		if len(jdata["args"]) != 1:
			print "Expected 1 argument, recieved "+len(jdata["args"])
			return

		queue.sremove(args[0])

	elif jdata["action"] == "pass":
		if len(jdata["args"]) not in [1, 2]:
			print "Expected at most 2 arguments, recieved "+len(jdata["args"])
			return

		queue.passoff(args[0], args[1] if len(args)>1 else 0)

	elif jdata["action"] == "spass":
		if len(jdata["args"]) != 1:
			print "Expected 1 argument, recieved "+len(jdata["args"])
			return

		queue.spass(args[0])

	elif jdata["action"] == "add":
		if len(jdata["args"]) != 4:
			print "Expected 4 arguments, recieved "+len(jdata["args"])
			return

		queue.append(args[0],args[1],args[2],args[3])
	else:
		print "Bad action name"


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
	return json.dumps(jdata)










