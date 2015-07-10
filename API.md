# LaserQueue API

This overview describes the API that binds the frontend and backend of the LaserQueue.

## Communication
Communication will be between some frontend user interface and the backend server using WebSockets. By default, we use port 8763 for this. Our frontend has a function, `socketSend()` that can be used to send things over WebSockets. It automatically adds the SID.

## Configuration
Our backend and frontend pull configuration info from a file, `www/config.json`. This file is created based on `www/defaultconf.json` by the backend server if it does not exist. It consists of JSON key-object pairs. Most should be self-explanatory. Some values, such as the version number and repository, should *not* be edited without a high level of knowledge. These files are in the `www/` directory so that they are accessible to the frontend over HTTP.

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

## Material types
The default material types with material codes in parentheses are:
- a: acrylic
- w: thin wood
- p: paper
- f: fabric
- c: cardboard
- tw: thick wood
- o: other

## Priorities
The default priority values with names in parentheses are:
- 0: "Lunch/after NuVu"
- 1: "Low"
- 2: "Normal"
- 3: "Important"
- 4: "Urgent"
- 5: "Absolutely Required"

## Actions:


### add
Adds the specified name, priority, etc to the list

#### Sample

```
{
	"action": "add",
	"args": [
		<name as Str>,
		<priority as Int>,
		<time in minutes as a Float or Int>,
		<material code as Str>
	],
	"sid": <SID>
}
```


### pass
Moves the specified job below the next job

#### Sample

```
{
	"action": "pass",
	"args": [
		<uuid of job as Str>
	],
	"sid": <SID>
}
```

### remove
Removes the specified job from the list

#### Sample

```
{
	"action": "remove",
	"args": [
		<uuid as Str>
	],
	"sid": <SID>
}
```

### move *
Moves the specified job to the target index, and the target priority

#### Sample

```
{
	"action": "move",
	"args": [
		<uuid of job as Str>,
		<target index as Int>,
		<target priority as Int>
	],
	"sid": <SID>
}
```


### relmove *
Moves the specified job to the target index in the master index. Out of bounds will default to the bounds.

#### Sample

```
{
	"action": "relmove",
	"args": [
		<uuid of job as Str>,
		<target index as Int>
	],
	"sid": <SID>
}
```


### increment *
Moves the specified job up one job, or if it's at the top of its priority level, up one priority.

#### Sample

```
{
	"action": "increment",
	"args": [
		<uuid of job as Str>
	],
	"sid": <SID>
}
```


### decrement *
Moves the specified job down one job, or if it's at the bottom of its priority level, down one priority.

#### Sample

```
{
	"action": "decrement",
	"args": [
		<uuid of job as Str>
	],
	"sid": <SID>
}
```


### attr
Sets the attribute of job uuid to value. if the config doesn't state that you can do it, you need auth. If it's an auth-requiring action, it applies the Modified gear.

#### Sample

```
{
	"action": "attr",
	"args": [
		<uuid of job as Str>,
		<key in job to change as Str>,
		<desired value>
	],
	"sid": <SID>
}
```


### auth
Enter admin mode if password is correct.

#### Sample

```
{
	"action": "auth",
	"args": [
		<sha1 hash of user-entered password as Str>
	],
	"sid": <SID>
}
```


### deauth
Leave admin mode.

#### Sample

```
{
	"action": "deauth",
	"sid": <SID>
}
```


### null
Nothing - however, the response will always be an up-to-date queue as JSON. This can be used to refresh the queue.

#### Sample

```
{
	"action": "null",
	"sid": <SID>
}
```

### shame
If you had a failed auth attempt, remove yourself from the deauths list to acknowledge that you have displayed a "wrong password" dialog.

#### Sample

```
{
	"action": "shame",
	"sid": <SID>
}
```


### refresh *
Refresh all users. Useful for pushing changes.  
Dependent upon config.allow_force_refresh.

#### Sample

```
{
	"action": "refresh",
	"sid": <SID>
}
```


### uuddlrlrba *
huehuehue  
Dependent upon config.easter_eggs.

#### Sample

```
{
	"action": "uuddlrlrba",
	"sid": <SID>
}
```

*: requires auth by default



## Data returned to client from backend
The action tag determines the data returned. The front end will receive these JSONs as responses, and should respond as specified.


### Display queue
This will be returned by the null action, or most calls that change the queue. The frontend should render the queue based on data in here. If in `deauths`, the frontend should call the `shame` action to acknowledge its shame (this is when an incorrect password hash has been received). If in `auths`, the frontend should make clear that the user is authed and therefore allowed to perform actions that require auth.

```
{
	"action": "display"
	"queue": <the queue object as List>.
	"auths": <the first halves of every authed sid as List>
	"deauths": <the first halves of every sid that failed to auth as List>
}
```

### Display modal
Displays a modal based on the packet.

```
{
	"action": "notification"
	"title": <the modal title as Str>
	"text": <the modal body as Str>
}
```


### Refresh the page
Dependent upon `config.allow_force_refresh`. The frontend should refresh itself fully. If a web interface, it should reload.

```
{
	"action":"refresh"
}
```

### Rickroll everyone.
The title says it all. Dependent upon `config.easter_eggs`.
```
{
	"action":"rickroll"
}
```
