# Plugins
Plugins can add features to the queue or tweak it to fit your needs. For general API info that may be relevant, see [API.md](../API.md).

## Frontend Plugin resources
Your JS will be concatenated with the other plugins. It has access to `formOptions`, a global object, to modify the form. The plugin should modify it as desired, then call `renderForm()` to make its changes reflected. There are two builtin types of form elements: strings for text and selects for dropdowns. Custom values are passed to the backend in the extras object.

### Events
Events get triggered on the `queueEvents` object when LaserQueue-related things happen. You can detect them with code like the example below, which displays an alert when the `auth` event gets triggered.

#### Example
```js
$(queueEvents).on('auth.success', function alertAuth() {
	alert('Auth event was triggered.');
});
```

#### Events list
| Event | Meaning |
|-------|---------|
|`auth.success`|User has successfully completed auth|
|`auth.failure`|User failed auth|
|`auth.deauth`|User logged out|
|`config.parsed`|Config file has been applied|
|`actions.populated`|Action buttons have been populated|
|`form.reset`|Built-in form elements have been cleared|
|`add.succeed`|Job was successfully added|
|`add.fail`|Job was not added|

### String form options
```js
formOptions.example = {
    "type": "string",
    "placeholder": "This is placeholder text",
    "tooltip": "This shows on hover",
    "classes": ["classes", "are", "added", "automatically"],
};
```

### Select form options
```js
formOptions.example = {
    "type": "select",
    "tooltip": "This shows on hover",
    "header": "An optional value. If set, this is added to the top of the dropdown, disabled but selected.",
    "options": [
      "This text goes in the dropdown",
      "The value returned is an index",
      "For this one it would be 2"
    ],
    "classes": ["classes", "are", "added", "automatically"],
};
```

Alternatively, `formOptions.example.options` can be an object with keys and values. In this case, the value returned to the backend will be the key.

### Generic form options
This enables custom form elements.
```js
formOptions.test = {
	"type": "generic",
	"template": "<button class='btn btn-default testButton'>testButton</button>",
	"getVal": function getVal() {
		return $('.testButton').html()
	}
};
```

## Backend Plugin resources
Two modules that have been made available you might find helpful:  
`ActionFramework` and `QueueConfig`.

`QueueConfig` is a clone of the normal `util` file, and `ActionFramework` supplies `SocketCommand`, `any_number`, and `any_type`.  

## Plugin Registry
`registry` is a `QueueObject.Registry` instance. If it exists in the module, it is considered to be a plugin. To register something, you call `QueueObject.Registry.register`. It currently has the following registrations handled:

* `"egg"`
* `"upkeep"`
* `"socket"`
* `"hideFromClient"`
* `"requiredTag"`
* `"requiredAuth"`
* `"attrDisable"`
* `"attrEnable"`
* `"attr"`
* `"initialPacket"`

### `"egg"`
Whenever a job is added, this will check if an easter egg is applicable.  
Format:
```python
{
  "match": [...],
  "serve": {...},
  "loud": "...",
  "broadcast": True|False
}
```

|Key|Type|Description|
|---|----|-----------|
|`match`|`list<str>`|A list of possible matches for the easter egg.|
|`serve`|`dict`|The packet to serve to the client when they submit the job.|
|`loud`|`str`|The text to output if `-v` was used to call the Queue.|
|`broadcast`|`bool`|Whether being in admin mode will broadcast this packet to everyone when you call it.|

### `"upkeep"`
Every `config.refreshRate` ms, this will be run. The object to register is a function accepting `**kwargs`.

|Key|Description|
|---|-----------|
|`queue`|The current `laserqueue.Queue` object.|
|`sessions`|The currect `sidhandler.SIDCache` object.|
|`sockets`|The current `backend.Sockets` object.|
|`registry`|The current `wireutils.Registry` object. Changes you make to this object will not be reflected elsewhere.|

### `"socket"`
This allows you to register commands for incoming socket data.
Format:
```python
"...",
function,
{...}
```
These are identical to the arguments for a `ActionFramework.SocketCommand` object.

### `"hideFromClient"`
This allows you to blacklist objects in a job from being sent to the frontend.
Format:
```python
"..."
```

### `"requiredTag"`
This allows you to add a key-data pair that all Queue jobs are initialized with.
Format:
```python
"...",
object
```

### `"requiresAuth"`
This allows you to blacklist a socket command name from being used by non-authenticated users.
Format:
```python
"..."
```

### `"attrDisable"`
This allows you to blacklist a tag from being edited with `attr`, even by authed users. Overrides the tag being present as an `attrEnable`.
Format:
```python
"..."
```

### `"attrEnable"`
This allows you to whitelist a tag in `attr` so that anyone can edit it.
Format:
```python
"..."
```

### `"attr"`
This allows you to register special behavior for a tag when it gets edited with `attr`.
Format:
```python
"...",
function
```
The function accepts `**kwargs`.

|Keyword|Type|Value|
|-------|----|-----|
|`value`|`object`|The target value for the tag.|
|`attrname`|`str`|The tag name.|
|`queue`|`laserqueue.Queue`|The queue.|
|`authstate`|`bool`|If the sender is authed.|
|`job`|`laserqueue.QueueObject`|The job that is being edited.|
|`masterindex`|`int`|The master index of the job.|
|`priority`|`int`|The priority of the job.|
|`index`|`int`|The index of the job.|

### `"initialPacket"`
Any packet registered this way will be sent to the frontend when it connects to the client.
Format:
```python
{
  "action": "...",
  ...
}
```
See [API.md](../API.md) for a list of acceptable packets. Plugins may register their own packets on the frontend.


## `ActionFramework.SocketCommand`
SocketCommand accepts these arguments:  
actionname, method, arglist

|Key|Description|
|---|-----------|
|`actionname`|A string which defines the object's name (and therefore action).|
|`method`|What function should be run when SocketCommand is intercepted.|
|`arglist`|A dictionary of arguments required and their types.|

Example:  
`SocketCommand("add", append, {"name": str, "priority": int, "time": any_number, "material": str})`  
where append is a function.  

Every method used for a SocketCommand should accept only `**kwargs`.

|Key|Type|Description|
|---|----|-----------|
|`args`|`dict`|All arguments in the json sent over the socket, minus `action`.|
|`authstate`|`bool`|Whether the session is authenticated.|
|`sec`|`str`|The identifier for the session, used to change/get its authstate.|
|`sessions`|`sidhandler.SIDCache`|The global session cache.|
|`ws`|`websockets.server.WebSocketServerProtocol`|The current session's socket.|
|`sockets`|`backend.Sockets`|All open sessions.|
|`queue`|`laserqueue.Queue`|The current queue.|
|`printer`|`util.Printer`|The printer instance for the main laserqueue.|
