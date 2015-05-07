// gets the config file and parses values

// declare almost all globals here
var getConfigFile, config, host, jsonData, socket, materials, priorities,  refreshRate, reconnectRate;
var allCuts = [];
var displayEl = {}
var renderDirectives = {
	priority: {
		html: function(params) {
			return this.priority + (
				this.coachmodified ? 
					' <span class="glyphicon glyphicon-cog coach-modified" data-toggle="tooltip" data-placement="bottom" title="' + getConfigFile.responseJSON['modified_hover'] + '"></span>'
					: ''
			);
		},
	}
};

// fetches config file from server
getConfigFile = $.getJSON('/config.json', function() {

	config = getConfigFile.responseJSON;

	// hide and disable log if not enabled
	devLog = getConfigFile.responseJSON["dev_log"];
	if(devLog != true) { $('[for=log-checkbox]').slideUp(); }

	// log entire config file
	logText("Config file follows:" + JSON.stringify(getConfigFile.responseJSON, null, 2));

	// set host from host and port
	host = "ws://" + getConfigFile.responseJSON["host"] + ":" + getConfigFile.responseJSON["port"];

	// set materials and priorities in the same way
	materials = getConfigFile.responseJSON["materials"];
	priorities = getConfigFile.responseJSON["priorities"].reverse();

	// set refreshRate and reconnectRate
	refreshRate = getConfigFile.responseJSON["refreshRate"];
	reconnectRate = getConfigFile.responseJSON["reconnectRate"];

	// render the materials dropdown
	for(var m in materials) {
		$('#cut-material').append('
			<option value="' + m + '">' + materials[m] + '</option>
		');
	}

	// render the priorities dropdown
	for(var p in priorities) {
		$('#priority-dropdown').append('
			<option value="' + p + '">' + priorities[p] + '</option>
		');
	}

});