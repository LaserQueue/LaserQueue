# Plugins
Plugins can add features to the queue or tweak it to fit your needs. For general API info that may be relevant, see [API.md](../API.md).

## Frontend Plugin resources
Your JS will be concatenated with the other plugins. It has access to `formOptions`, a global object, to modify the form. The plugin should modify it as desired, then call `renderForm()` to make its changes reflected. There are two builtin types of form elements: strings for text and selects for dropdowns. Custom values are passed to the backend in the extras object.

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

## Backend Plugin functions
Each plugin must have at least one of these:
### Event Registry
`eventRegistry` is a `QueueObject.Registry` instance. To register an event, you call `QueueObject.on`. It currently has the following events handled:

#### `"egg"`
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
* `match` is a list of possible matches for the easter egg.  
* `serve` is the packet to serve to the client when they submit the job.  
* `loud` is the text to output if `-v` was used to call the Queue.  
* If `broadcast` is true, being in admin mode will broadcast this packet to everyone when you call it.

#### `"upkeep"`
Every `config.refreshRate` ms, this will be run. The object to register is a function accepting `**kwargs`. These args are, at the moment:
* `queue` - The current `laserqueue.Queue` object
* `sessions` - The currect `sidhandler.SIDCache` object
* `sockets` - The current `main.Sockets` object
* `reg` - The current `wireutils.Registry` object. Changes you make to this object will not be reflected elsewhere.

#### `"socket"`
This allows you to register commands for incoming socket data.
Format:
```python
(
  "...",
  function,
  {...}
)
```
These are identical to the arguments for a `ActionFramework.SocketCommand` object.
### Hidden from the client
`hideFromClient` is a list of tags to be added to the blacklist in `QueueObject.serialize`.
### Required tags
`requiredTags` is a dict of tags required for QueueObjects. Merged under the existing.
### Auth-requiring actions
`requiresAuth` is a list of names of commands that require auth.

## `ActionFramework.SocketCommand`
SocketCommand accepts these arguments:  
actionname, method, arglist
* `actionname` is a string which defines the object's name (and therefore action).
* `method` is what function should be run when SocketCommand is intercepted.
* `arglist` is a dictionary of arguments required and their types.

Example:  
`SocketCommand("add", append, {"name": str, "priority": int, "time": any_number, "material": str})`  
where append is a function.  

Every method used for a SocketCommand should accept only **kwargs. These are the things passed currently:
* `args`: a dictionary of all arguments in the json sent over the socket, minus `action`.
* `authstate`: a boolean that contains whether the session is authenticated.
* `sec`: the identifier for the session, used to change/get its authstate.
* `sessions`: the global instance of sidhandler.SIDCache.
* `ws`: the websocket for this session.
* `sockets`: a main.Sockets object that contains all the current sessions.
* `queue`: the laserqueue.Queue object holding the jobs.

## Printing
Unlike in a normal program, you shouldn't just edit `color_printing_config`. This will edit the process's `color_printing_config`, meaning that the `[Backend]` in the log will become your plugin's name. Instead, you use `PluginPrinterInstance`, included in `QueueConfig`.  

`PluginPrinterInstance` can emulate any function of color_print. You may pass it an existing `color_config` when you make it. If you don't, it will be a blank one.  
You can use `PluginPrinterInstance.colorconfig` to change the name and color, or you can call `PluginPrinterInstance.setname(string)` or `PluginPrinterInstance.setcolor(string)` to do it for you.  
To print/get input, use `PluginPrinterInstance.color_print` and `PluginPrinterInstance.color_input`. They function exactly like the other ones, but they aren't affected by the "colorconfig" argument.
