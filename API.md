
comm protocols

Sending to server

Format:
{
	"action": action to perform
	"args": list of arguments
	"sid": your session ID.
}

actions:


add
arguments: name, priority, estimated time, material code

adds the specified name, priority, etc to the list.


pass
arguments: uuid

moves the specified job below the next job.


remove
arguments: uuid

removes the specified job from the list.


move *§
arguments: uuid, target index, target priority

moves the specified job to the target index, and the target priority.


relmove *§
arguments: uuid, target index

moves the specified job to the target index in the master index. Out of bounds will default to the bounds.


increment *§
arguments: uuid

moves the specified job up one job, or if it's at the top of its priority level, up one priority.


decrement *§
arguments: uuid

moves the specified job down one job, or if it's at the bottom of its priority level, down one priority.


attr 
arguments: uuid, attribute, value

sets the attribute of job uuid to value. if the config doesn't state that you can do it, you need auth. If it's an auth-requiring action, it applies the Modified gear.


auth
arguments: sha1 hash of password

enter admin mode if password is correct.


deauth
arguments: N/A

leave admin mode.


null
arguments: N/A

nothing


shame
arguments: N/A

if you had a failed auth attempt, remove yourself from the deauths list.


refresh
arguments: N/A

refresh all users. Useful for pushing changes.
dependent upon config.allow_force_refresh.


uuddlrlrba §
arguments: N/A

huehuehue
dependent upon config.easter_eggs.


*: applies the Modified gear.
§: requires auth by default.


Sending to client:

the action tag defines the data sent.


display
{
	"action": "display"
	"queue": the queue object.
	"auths": a list of the first halves of every auth'd sid.
	"deauths": a list of the first halves of every sid that failed to auth.
}

refresh the page.
dependent upon config.allow_force_refresh
{
	"action":"refresh"
}

rickroll everyone.
dependent upon config.easter_eggs
{
	"action":"rickroll"
}