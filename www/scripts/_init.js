// initialize the things

// holds old and new JSON
// for comparison to minimize layout thrashing n stuff
var oldJsonData = "uninitialized";
var jsonData;

// start message & websockets host
logText("LaserCutter software is up. Attempting connection to WebSockets host", host);

// initialize websockets
var socket = new WebSocket(host);

// initialize action row
populateActions();

// initialize bootstrap tooltips
$(function () {
	$('[data-toggle="tooltip"]').tooltip()
});

// initialize the modal by changing the title
$('.notify-modal-title').html("Notification");