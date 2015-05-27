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

// authentication modal
$('.nuvu-logo').click(function() {
	modalMessage('Authenticate', '
		<form class="login-form">
			<div class="form-group">
				<label for="password">Password</label>
				<input type="password" class="form-control" id="password" placeholder="Password">
			</div>
			<button type="submit" class="btn btn-default">Sign in</button>
		</form>
	');
	$('.login-form').submit(function(event) {
		event.preventDefault();
		if($('#password').val() !== "imacoach") {
			modalMessage("WHO DO YOU THINK YOU ARE", "I understand. You found paradise in America, you had a good trade, you made a good living. The police protected you and there were courts of law. You didn't need a friend like me. But, now you come to me, and you say: \"LaserQueue, give me justice.\" But you don't ask with respect. You don't offer friendship. You don't even think to call me Godfather. Instead, you come into my house on the day my daughter is to be married, you tell me you're a coach, and you LIE TO ME.");
		} else {
			coachMode();
		}
	});
});

// footer
$.ajax({
	url: '/infotext.md',
	type: 'GET'
})
.done(function(request) {
	$('.credits-footer').before(marked(request));
})
.fail(function() {
	console.log("Failed to get infotext.md");
});
