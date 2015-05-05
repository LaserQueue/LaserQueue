// gets the config file and parses values

// declare almost all globals here
var getConfigFile, host, jsonData, socket, materials, priorities, refreshRate, reconnectRate;
var fullList = [];

// fetches config file from server
getConfigFile = $.getJSON('/config.json', function() {
	// set host from host and port
	host = "ws://" + getConfigFile.responseJSON["host"] + ":" + getConfigFile.responseJSON["port"];

	// set materials and priorities in the same way
	materials = getConfigFile.responseJSON["materials"];
	priorities = getConfigFile.responseJSON["priorities"].reverse();

	// set refreshRate and reconnectRate
	refreshRate = getConfigFile.responseJSON["refreshRate"];
	reconnectRate = getConfigFile.responseJSON["reconnectRate"];

	// log entire config file
	logText("Config file follows:" + JSON.stringify(getConfigFile.responseJSON, null, 2));
});

// pull table's first row out for insertion later
var tableFirstRow = $(".cutting-table").html();