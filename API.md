# LaserQueue API

This overview describes the API that binds the frontend and backend of the LaserQueue.

## Communication
Communication will be between some frontend user interface and the backend server using WebSockets. By default, we use port 8763 for this.

## Data format
JSON formatted as follows:
```
{
	"action": action to perform
	"args": [list, of, Arguments]
	"sid": your session ID.
}
```

## Session ID
Each active user has a session ID, a 128-bit unique key. This UUID should be generated at the beginning of a session and sent with every packet except for data refreshes with {"action": "null"}.

## Actions:


### add
Arguments: name, priority, estimated time, material code

Adds the specified name, priority, etc to the list


### pass
Arguments: uuid

Moves the specified job below the next job


### remove
Arguments: uuid

Removes the specified job from the list


### move *
Arguments: uuid, target index, target priority

Moves the specified job to the target index, and the target priority


### relmove *
Arguments: uuid, target index

Moves the specified job to the target index in the master index. Out of bounds will default to the bounds.


### increment *
Arguments: uuid

Moves the specified job up one job, or if it's at the top of its priority level, up one priority.


### decrement *
Arguments: uuid

Moves the specified job down one job, or if it's at the bottom of its priority level, down one priority.


### attr 
Arguments: uuid, attribute, value

Sets the attribute of job uuid to value. if the config doesn't state that you can do it, you need auth. If it's an auth-requiring action, it applies the Modified gear.


### auth
Arguments: sha1 hash of user-entered password

Enter admin mode if password is correct.


### deauth
Arguments: N/A

Leave admin mode.


### null
Arguments: N/A

Nothing - however, the response will always be an up-to-date queue as JSON. This can be used to refresh the queue.

### shame
Arguments: N/A

If you had a failed auth attempt, remove yourself from the deauths list to acknowledge that you have displayed a "wrong password" dialog.


### refresh *
Arguments: N/A

Refresh all users. Useful for pushing changes.
Dependent upon config.allow_force_refresh.


### uuddlrlrba *
Arguments: N/A

huehuehue
Dependent upon config.easter_eggs.

*: requires auth by default



## Data returned to client (data to send from backend):
The action tag determines the data returned.


### Display queue
This will be returned by null, or most calls that change the queue.

```
{
	"action": "display"
	"queue": the queue object.
	"auths": a list of the first halves of every auth'd sid.
	"deauths": a list of the first halves of every sid that failed to auth.
}
```


### Refresh the page
Dependent upon config.allow_force_refresh

```
{
	"action":"refresh"
}
```

### Rickroll everyone.

```
Dependent upon config.easter_eggs
{
	"action":"rickroll"
}
```