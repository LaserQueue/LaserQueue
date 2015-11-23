function Command(match, execute) {
	if (!isCommandDefinition(match)) throw "Invalid command. ({match})".format(match)
	this.match = match;
	var cmdname = match.match(/^[\$#]\s*\w+\b/)[0];
	this.name = cmdname.match(/\w+/)[0];
	this.level = ;

	this.docstr = "Usage: "+match;
	this.execute = execute;
}

/**
 * Argument types:
 * <name> -> required arg (you may not have any of these after a required arg)
 * [name] -> optional arg
 * [*literal] -> optional literal (passed as a true/false)
 * ... -> capture all remaining data as literal
 * literal -> catch as literal
 * 
 * a command must follow either of the following formats
 * commands prepended with # are only runnable as admin
 * commands not prepended with # must be prepended with $
 * names must only be comprised of characters that match /\w/
 */
function isCommandDefinition(string) {
	string = string.trim();
	var name = string.search(/^[\$#]\s*\w+\b/);
	if (name === -1) return false;

	string = string.replace(/^[\$#]\s*\w+\b/, "");
	var keys = string.trim().split(/\s+/);
	var optflag = false;
	var captureflag = false;
	for (index in keys) {
		key = keys[index];
		if (key.search(/^\[\*?\w+\]$/) !== -1) {
			optflag = true;
			if (captureflag) return false;
		} else if (key.search(/^\.\.\.$/) !== -1) {
			captureflag = true;
			if (captureflag) return false;
		} else if (key.search(/^(\w+|<\w+>)$/) !== -1) {
			if (captureflag || optflag) return false;
		} else if (key) {
			return false;
		}
	}
	return true;
}

function parseCommandDefinition(string) {
	if (!isCommandDefinition(string)) return null;

	var ret = {level: 0, name: '', args: []};

	string = string.trim();
	var name = string.match(/^[\$#]\s*\w+\b/)[0];
	ret.name = name.replace(/[\$#]\s*/, "");
	ret.level = name[0] == "#" ? 1 : 0;

	string = string.replace(/^[\$#]\s*\w+\b/, "");
	var keys = string.trim().split(/\s+/);

	for (index in keys) {
		key = keys[index];
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

Command.prototype.toString = function toString() {
	return this.match;
}

Command.prototype.setDocstr = function setDocstr(string) {
	this.docstr = string.replace(/%s/, this.match)
};

Command.prototype.parse = function parse(inp) {

};
