#!/usr/bin/env node

// config.json + defaultconf.json + config-doc.json --> config.md

var fs = require('fs');
var date = new Date();

// fetch ALL OF THE JSON
var config = JSON.parse(fs.readFileSync('./config.json', 'utf8'));
var defaultConf = JSON.parse(fs.readFileSync('./defaultconf.json', 'utf8'));
var configDoc = JSON.parse(fs.readFileSync('./config-doc.json', 'utf8'));

// string formatting function
String.prototype.format = function formatString() {
	var str = this.toString();
	if (!arguments.length)
		return str;
	var args = typeof arguments[0];
	args = (("string" == args || "number" == args) ? arguments : arguments[0]);
	for (var arg in args)
		str = str.replace(RegExp("\\{" + arg + "\\}", "gi"), args[arg]);
	return str;
};

// print documentation header
console.log(
    '# config.json reference\n'
    + 'This file documents `config.json`, the LaserQueue configuration file.\n'
    + '## Notes\n'
    + '- `config.json` is a standard JSON key/value store\n'
    + '- The config is generated from `defaultconf.json` when the queue first runs. Running the queue again with the `-r` flag will regenerate it.\n'
    + '- Both the frontend and backend rely on and can access values in `config.json`. The backend can change these values.\n'
    + '- The file is stored in the `www` directory so that the frontend can access it\n'
    + '## Keys and values\n'
);

// for each config value
for(var i  in config) {
	// check if param is an array
	var parameterType = (config[i].constructor === Array ? 'array' : typeof config[i]);

	// print key and type as third-level header
	console.log('### `{key}` : `{type}`'.format({
        key: i,
        type: parameterType
    }));

	// if config-doc.json has a note, print it
	if (configDoc[i]) console.log(configDoc[i]);

	// print default value as 4th-level header
	console.log('#### Default: `{default}`'.format({
        default: defaultConf[i]
    }));

	// print break
    console.log('---');
}

console.log('This file automatically generated at {timestamp}'.format({timestamp: date}));

return exitCode;
