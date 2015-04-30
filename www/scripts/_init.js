// initialize the things

window.console.log("This silly browser log is generally not used. Click the console button at the bottom of the page instead! If there are errors here, please raise an issue.");

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