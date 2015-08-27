#!/usr/bin/env node

// generates documentation based on config.json and defaultconf.json

var fs = require('fs');
var date = new Date();

var exitCode = 0;

var config = JSON.parse(fs.readFileSync('./config.json', 'utf8'));
var defaultConf = JSON.parse(fs.readFileSync('./defaultconf.json', 'utf8'));
var configDoc = JSON.parse(fs.readFileSync('./config-doc.json', 'utf8'));

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

for(var i  in config) {
    console.log('### `{key}` : `{type}`'.format({
        key: i,
        type: typeof config[i]
    }));
    if (configDoc[i]) console.log(configDoc[i]);
    console.log('#### Default: `{default}`'.format({
        default: defaultConf[i]
    }));
    console.log('---');
}

console.log('This file automatically generated at {timestamp}'.format({timestamp: date}));

return exitCode;
