function Command(match, execute) {
	if (isNotCommandDefinition(match)) throw "Invalid command. ({match})".format({match: match});
	this.match = match;
	var definition = parseCommandDefinition(match);
	if (typeof definition === 'string') definition = {};
	this.command = definition;
	this.name = definition.name;
	this.docstr = "Usage: "+match;
	this.execute = execute;
}

Command.prototype.toString = function toString() {
	return this.match;
};

Command.prototype.setDocstr = function setDocstr(string) {
	this.docstr = string.replace(/%s/, this.match);
};

Command.prototype.parse = function parse(inp) {
	var inpParsed = extractCommand(inp);
	if (typeof inpParsed === 'string') return inpParsed;
	var args = matchArguments(this.command, inpParsed, true);
	return args;
};

var localize = {
	"error.badName": "Invalid function definition.",
	"error.argAfterSplat": "Argument found after ... was used.",
	"error.posAfterOpt": "Found a positional argument after an optional one was used.",
	"error.inString": "Unbalanced strings.",
	"error.missingLiteral": "Missing a literal in the command call.",
	"error.badLiteral": "Invalid argument for optional literal.",
	"error.badAction": "Bad command definition.",
	"error.extraneousArguments": "Too many arguments."
};
function translate(inp) {
	if (localize.hasOwnProperty(inp)) return localize[inp];
	else return inp;
}

Command.prototype.run = function run(inp) {
	var parsed = this.parse(inp);
	if (typeof parsed === 'string') logText("[ERROR] "+translate(parsed));
	else if (parsed === null) return false;
	else if (typeof parsed === 'object') {
		var output = this.execute(parsed);
		if (typeof output === 'object') return output;
		return true;
	}
	return false;
};

function CommandExecutor(commands) {
	if (typeof commands === 'undefined') this.commands = [];
	else this.commands = commands;
}

CommandExecutor.prototype.push = function push(cmd) {
	this.commands.push(cmd);
};

CommandExecutor.prototype.run = function run(inp) {
	var shallowCommands = this.commands.slice();
	shallowCommands.reverse();
	for (var commandindex in shallowCommands) {
		var command = shallowCommands[commandindex];
		var output = command.run(inp);
		if (typeof output === 'object') {
			socketSend(output);
			return true;
		} else if (output) return true;
	}
	return false;
};

CommandExecutor.prototype.runIntercept = function run(inp) {
	var shallowCommands = this.commands.slice();
	shallowCommands.reverse();
	for (var commandindex in shallowCommands) {
		var command = shallowCommands[commandindex];
		var output = command.run(inp);
		if (typeof output === 'object') {
			return output;
		} else if (output) return true;
	}
	return false;
};


// argument types:
// <name> -> required arg (you may not have any of these after a required arg)
// [name] -> optional arg
// [*literal] -> optional literal (passed as a true/false)
// ... -> capture all remaining data as literal
// literal -> catch as literal

// a command must follow either of the following formats
// commands prepended with # are only runnable as admin
// commands not prepended with # must be prepended with $
// names must only be comprised of characters that match /\w/
 
function isNotCommandDefinition(string) {
	string = string.trim();
	var name = string.search(/^[\$#]\s*\w+\b/);
	if (name === -1) return "error.badName";

	string = string.replace(/^[\$#]\s*\w+\b/, "");
	var keys = string.trim().split(/\s/);
	var optflag = false;
	var captureflag = false;
	for (var index in keys) {
		var key = keys[index];
		if (key.search(/^\[\*?\w+\]$/) !== -1) {
			optflag = true;
			if (captureflag) return "error.argAfterSplat";
		} else if (key.search(/^\.\.\.$/) !== -1) {
			if (captureflag) return "error.argAfterSplat";
			captureflag = true;
		} else if (key.search(/^(\w+|<\w+>)$/) !== -1) {
			if (captureflag || optflag) return "error.posAfterOpt";
		} else if (key) {
			return "error.badKey";
		}
	}
	return "";
}

function parseCommandDefinition(string) {
	if (isNotCommandDefinition(string)) return isNotCommandDefinition(string);

	var ret = {level: 0, name: '', args: []};

	string = string.trim();
	var name = string.match(/^[\$#]\s*\w+\b/)[0];
	ret.name = name.replace(/[\$#]\s*/, "");
	ret.level = name[0] === "#" ? 1 : 0;

	string = string.replace(/^[\$#]\s*\w+\b/, "");
	var keys = string.trim().split(/\s+/);

	for (var index in keys) {
		var key = keys[index];
		if (key.search(/^\[\w+\]$/) !== -1) {
			ret.args.push({
				name: key.match(/\w+/)[0],
				type: 'opt'
			});
		} else if (key.search(/^\[\*\w+\]$/) !== -1) {
			ret.args.push({
				name: key.match(/\w+/)[0],
				type: 'optlit'
			});
		} else if (key.search(/^\.\.\.$/) !== -1) {
			ret.args.push({
				name: 'remaining',
				type: 'splat'
			});
		} else if (key.search(/^<\w+>$/) !== -1) {
			ret.args.push({
				name: key.match(/\w+/)[0],
				type: 'req'
			});
		} else if (key.search(/^\w+$/) !== -1) {
			ret.args.push({
				name: key.match(/\w+/)[0],
				type: 'lit'
			});
		}
	}
	return ret;
}

function extractCommand(string) {
	var inString = false;
	var currentString = "";
	var stringArgs = [];
	var keys = string.trim().split(/\s+/);
	for (var index in keys) {
		var key = keys[index];
		if (!inString && key.search(/^(\\\\)*\"[^((\\\\)*\")]/) !== -1) {
			inString = true;
			currentString += key.replace(/^\\?\"/, "") + " ";
		} else if (inString) {
			if (key.search(/[^((\\\\)*\")](\\\\)*\"/) !== -1) {
				inString = false;
				stringArgs.push((currentString + key.replace(/\\?\"$/, "")).replace(/\\\"/, '"'));
				currentString = "";
			} else {
				currentString += key + " ";
			}
		} else {
			stringArgs.push(key.replace(/\\\"/, '"'));
		}
	}
	if (inString) return "error.inString";
	return stringArgs;
}

function matchArguments(command, args, safe) {
	var ret = {};
	if (command.name !== args[0]) {
		if (!safe) return "error.incorrectName";
		else return null;
	}
	var splatted = false;
	var argindex;
	for (argindex in command.args) {
		var arg = command.args[argindex];
		var inparg = args[+argindex+1];
		if (arg.type === 'lit') {
			if (inparg !== arg.name) {
				if (!safe) return "error.missingLiteral";
				else return null;
			}
		} else if (arg.type === 'req' || arg.type === 'opt') {
			ret[arg.name] = inparg;
		} else if (arg.type === 'optlit') {
			if (inparg !== arg.name && inparg !== null) {
				ret[arg.name] = null;
			} else {
				if (!safe) return "error.badLiteral";
				else return null;
			}
		} else if (arg.type === 'splat') {
			splatted = true;
			ret[arg.name] = args.slice(+argindex+1).join(" ");
		} else {
			if (!safe) return "error.badAction";
			else return null;
		}
	}
	if (argindex < args.length-2 && !splatted) {
		if (!safe) return "error.extraneousArguments";
		else return null;
	}
	return ret;
}

$('.command-line').keydown(function onKeyPress(event) {
	if (event.which == 13) {
		event.preventDefault();
		var text = $('.command-line').val();
		if (text) {
			if (!commands.run(text)) logText("[ERROR] Invalid command.");
			$('.command-line').val("");
		}
	}
});
