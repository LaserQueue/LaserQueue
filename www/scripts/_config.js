// gets the config file and parses values


var host, socket, materials, priorities, refreshRate, reconnectRate;

// fetches config file from server
var getConfigFile = $.getJSON('/config.json', function() {
	host = String("ws://" + getConfigFile.responseJSON["host"] + ":" + getConfigFile.responseJSON["port"]);
});

// pull table's first row out for insertion later
var tableFirstRow = $(".cutting-table").html();

// list of materials
var materials = {
	"w": "Thin Wood",
	"tw": "Thick Wood",
	"c": "Cardboard",
	"a": "Acrylic",
	"p": "Paper",
	"f": "Fabric",
	"o": "Other"
};

// list of priorities
var priorities = [
	"Lunch/After NuVu",
	"Low", 
	"Normal",
	"Important",
	"Urgent",
	"Absolutely Required"
].reverse();

var refreshRate = 200;
