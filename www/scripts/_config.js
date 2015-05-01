// gets the config file and parses values


var host, socket, materials, priorities, refreshRate, reconnectRate;

// fetches config file from server
var getConfigFile = $.getJSON('/config.json', function() {
	host = "ws://" + getConfigFile.responseJSON["host"] + ":" + getConfigFile.responseJSON["port"];

	materials = getConfigFile.responseJSON["materials"];
	priorities = getConfigFile.responseJSON["priorities"].reverse();
	logText("Config file follows:" + JSON.stringify(getConfigFile.responseJSON, null, 2));
});

// pull table's first row out for insertion later
var tableFirstRow = $(".cutting-table").html();

var refreshRate = 200;
