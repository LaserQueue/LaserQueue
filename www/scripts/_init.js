// initialize the things

window.console.log("This silly browser log is generally not used. Click the console button at the bottom of the page instead! If there are errors here, please raise an issue.");

setInterval(function() {
	if(typeof reconnectRate != "undefined" && (typeof socket == "undefined" || socket.readyState == socket.CLOSED)) {
		// initialize websockets if closed
		logText("LaserCutter software is up. Attempting connection to WebSockets host", host);
		socketSetup();
	}
}, reconnectRate);

// holds old and new JSON
// for comparison to minimize layout thrashing n stuff
var oldJsonData = "uninitialized";
var jsonData;

// initialize the modal by changing the title
$('.notify-modal-title').html("Notification");
