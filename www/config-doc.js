#!/usr/bin/env node

// config.json + defaultconf.json + config-doc.json --> config.md

var fs = require('fs');
var date = new Date();

var out = "";

// fetch ALL OF THE JSON
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
out += '# config.json reference\n'
				+ 'This file documents `config.json`, the LaserQueue configuration file.\n'
				+ '## Notes\n'
				+ '- `config.json` is a standard JSON key/value store\n'
				+ '- The config is generated from `defaultconf.json` when the queue first runs. Running the queue again with the `-r` flag will regenerate it.\n'
				+ '- Both the frontend and backend rely on and can access values in `config.json`. The backend can change these values.\n'
				+ '- The file is stored in the `www` directory so that the frontend can access it\n'
				+ '## Keys and values\n\n';

// for each config value
keys = Object.keys(defaultConf).sort();
for(var iindex in keys) {
	// check if param is an array
	var i = keys[iindex];
	var parameterType = (defaultConf[i].constructor === Array ? 'array' : typeof defaultConf[i]);

	// print key and type as third-level header
	out += '### `{key}` : `{type}`\n'.format({
				key: i,
				type: parameterType
		});

	// if config-doc.json has a note, print it
	if (configDoc[i]) out += configDoc[i]+"\n";

	// print default value as 4th-level header
	out += '#### Default: `{default}`\n'.format({
				default: defaultConf[i]
		});

	// print break
		out += '---\n';
}

out += 'This file automatically generated at {timestamp}'.format({timestamp: date});

console.log(out);

fs.writeFile('config.md', out, function (err) {
  if (err) throw err;
});
