function Command(match, execute) {
	if (!isCommandDefinition(match)) throw "Invalid command. ({match})".format(match);
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
	if (typeof inpParsed === 'string') inpParsed = [];
	var args = matchArguments(this.command, inpParsed);
	if (typeof args === 'string') args = {};
	return args;
};

Command.prototype.matches = function matches(inp) {
	var inpParsed = extractCommand(inp);
	if (typeof inpParsed === 'string') inpParsed = [];
	var args = matchArguments(this.command, inpParsed);
	return typeof args !== 'string';
};

Command.prototype.run = function run(inp) {
	if (this.matches(inp)) {
		return this.execute(this.parse(inp));
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
 
function isCommandDefinition(string) {
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
			captureflag = true;
			if (captureflag) return "error.argAfterSplat";
		} else if (key.search(/^(\w+|<\w+>)$/) !== -1) {
			if (captureflag || optflag) return "error.posAfterOpt";
		} else if (key) {
			return "error.badKey";
		}
	}
	return "";
}

function parseCommandDefinition(string) {
	if (isNotCommandDefinition(string)) return isCommandDefinition(string);

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

function matchArguments(command, args) {
	var ret = {};
	for (var argindex in command.args) {
		var arg = command.args[argindex];
		var inparg = args[argindex];
		if (!argindex) {
			if (command.name !== inparg) {
				return "error.incorrectName";
			}
		} else if (arg.type === 'lit') {
			if (inparg !== arg.name) {
				return "error.missingLiteral";
			}
		} else if (arg.type === 'req' || arg.type === 'opt') {
			ret[arg.name] = inparg;
		} else if (arg.type === 'optlit') {
			if (inparg !== arg.name && inparg !== null) {
				ret[arg.name] = null;
			} else {
				return "error.badLiteral";
			}
		} else if (arg.type === 'splat') {
			ret[arg.name] = args.slice(argindex+1).join(" ");
		} else {
			return "error.badAction";
		}
	}
	return ret;
}
