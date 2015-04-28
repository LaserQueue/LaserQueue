// gets the config file and parses values


// fetches config file from server
var configFile = $.getJSON('/config.json', function(json, textStatus) {

}).fail(function() {
	modalMessage('Error 3', 'Could not find or parse config file. Have you initialized your configuration using start.sh? See <a href="https://github.com/yrsegal/LaserQueue/blob/master/README.md">the README</a> for more info');
});

console.log(configFile.responseJSON);

// WebSockets host
var host = "ws://yrsegal.local:8765";

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
