# LaserQueue API

This overview describes the API that binds the frontend and backend of the LaserQueue. For info related to plugins, please see [plugins/plugins.md](plugins.md) in the plugins folder.


## Communication
```
         ┌──────────────────────────────┐
         │                              │
      ┌─▶│     LaserQueue frontend      │
      │  │                              │
      │  └──────────────────────────────┘
      │                  ▲               
  Website                │               
   hosted            JSON over           
 over HTTP          WebSockets           
      │                  │               
      │                  ▼               
      │  ┌──────────────────────────────┐
      │  │                              │
      └──│      LaserQueue backend      │
         │                              │
         └──────────────────────────────┘
```
Communication will be between some frontend user interface and the backend server using WebSockets. By default, we use port 8763 for this. Our frontend has a function, `socketSend()` that can be used to send JSON over WebSockets.

## Configuration
Our backend and frontend pull configuration info from a file, `www/config.json`. This file is created based on `www/defaultconf.json` by the backend server if it does not exist. It consists of JSON key-object pairs. Most should be self-explanatory. Some values, such as the version number and repository, should *not* be edited without a high level of knowledge. These files are in the `www/` directory so that they are accessible to the frontend over HTTP.

## Data format
JSON formatted as follows:
```
{
	"action": action to perform
	...
}
```

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
	"name": <name as Str>,
	"priority": <priority as Int>,
	"time": <time in minutes as a Float or Int>,
	"material": <material code as Str>
}
```

#### add: Optional arguments

`extras` is an object of extra key/value pairs to add to the queue object. This is meant to be used by plugins wishing to add custom data to the queue object.

##### Sample

```
{
	"action": "add",
	"name": <name as Str>,
	"priority": <priority as Int>,
	"time": <time in minutes as a Float or Int>,
	"material": <material code as Str>,
	"extras": {
		<key as Str>: <associated data>,
		...
	}
}
```


### pass
Moves the specified job below the next job

#### Sample

```
{
	"action": "pass",
	"uuid": <uuid of job as Str>
}
```

### remove
Removes the specified job from the list

#### Sample

```
{
	"action": "remove",
	"uuid": <uuid of job as Str>
}
```

### move *
Moves the specified job to the target index, and the target priority

#### Sample

```
{
	"action": "move",
	"uuid": <uuid of job as Str>,
	"target_index": <target index as Int>,
	"target_priority": <target priority as Int>
}
```


### relmove *
Moves the specified job to the target index in the master index. Out of bounds will default to the bounds.

#### Sample

```
{
	"action": "relmove",
	"uuid": <uuid of job as Str>,
	"target_index": <target index as Int>
}
```


### increment *
Moves the specified job up one job, or if it's at the top of its priority level, up one priority.

#### Sample

```
{
	"action": "increment",
	"uuid": <uuid of job as Str>
}
```


### decrement *
Moves the specified job down one job, or if it's at the bottom of its priority level, down one priority.

#### Sample

```
{
	"action": "decrement",
	"uuid": <uuid of job as Str>
}
```


### attr
Sets the attribute of job uuid to value. if the config doesn't state that you can do it, you need auth. If it's an auth-requiring action, it applies the Modified gear.

#### Sample

```
{
	"action": "attr",
	"uuid": <uuid of job as Str>,
	"key": <key in job to change as Str>,
	"new": <desired value>
}
```


### auth
Enter admin mode if password is correct. Dependent upon `config.admin_mode_enabled`.

#### Sample

```
{
	"action": "auth",
	"pass": <sha1 hash of user-entered password as Str>
}
```


### deauth
Leave admin mode. Dependent upon `config.admin_mode_enabled`.

#### Sample

```
{
	"action": "deauth"
}
```


### refresh *
Refresh all users. Useful for pushing changes.  
Dependent upon config.allow_force_refresh.

#### Sample

```
{
	"action": "refresh"
}
```


### uuddlrlrba *
huehuehue  
Dependent upon config.easter_eggs.

#### Sample

```
{
	"action": "uuddlrlrba"
}
```

*: requires auth by default



## Data returned to client from backend
The action tag determines the data returned. The front end will receive these JSONs as responses, and should respond as specified.


### Display queue
The frontend should render the queue based on data in here.

```
{
	"action": "display",
	"queue": <the queue object as List>
}
```

### Display modal
Displays a modal based on the packet.

```
{
	"action": "notification",
	"title": <the modal title as Str>,
	"text": <the modal body as Str>
}
```

### Authed
Called when the sid gains authstate. Dependent upon `config.admin_mode_enabled`.

```
{
	"action":"authed"
}
```

### Auth faliure
Called when auth finds a wrong password. Dependent upon `config.admin_mode_enabled`.

```
{
	"action":"authfailed"
}
```

### Deauthed
Called when the sid loses its authstate. Dependent upon `config.admin_mode_enabled`.

```
{
	"action":"deauthed"
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
