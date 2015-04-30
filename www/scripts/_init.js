// initialize the things

// gets the config file and parses values

var host, socket;

// fetches config file from server
var getConfigFile = $.getJSON('/config.json', function() {
	host = String("ws://" + getConfigFile.responseJSON["host"] + ":" + getConfigFile.responseJSON["port"]);
});

setInterval(function() {
	if(typeof socket == "undefined" || socket.readyState == socket.CLOSED) {
		// initialize websockets if closed
		logText("LaserCutter software is up. Attempting connection to WebSockets host", host);
		socketSetup();
	}
}, refreshRate);

// holds old and new JSON
// for comparison to minimize layout thrashing n stuff
var oldJsonData = "uninitialized";
var jsonData;

// initialize action row
populateActions();

// initialize bootstrap tooltips
$(function () {
	$('[data-toggle="tooltip"]').tooltip()
});

// initialize the modal by changing the title
$('.notify-modal-title').html("Notification");