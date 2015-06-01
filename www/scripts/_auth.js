function auth() {
	authed = true;
	logText('Displaying authed modal.');
	modalMessage('Success!', '<p class="lead">You\'ve been authorized!</p>');
	$('.disabled').prop('disabled', false);
}

function failedauth() {
	modalMessage('Failure', '<p class="lead">Unfortunately, it looks like your password was wrong.</p>');
	logText('Password was wrong. Added to deauths. Shame activated. You\'re bad and you should feel bad.');
	socket.send(JSON.stringify({'action':'shame','sid': SID}));
}

function deauth() {
	authed = false;
	logText('User has been deauthed.');
	$('.disabled').prop('disabled', true);
}