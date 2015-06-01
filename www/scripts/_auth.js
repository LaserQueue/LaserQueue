function auth() {
	for(i in jsonData.auths) {
		if(jsonData.auths[i] == SID.substring(0, 18)) {
			logText('User has been authed.');
			authed = true;
		}
	}

	if(authed) {
		logText('Displaying authed modal.');
		modalMessage('Success!', '<p class="lead">You\'ve been authorized!</p>');
		$('.disabled').prop('disabled', false);
	} else {
		modalMessage('Failure', '<p class="lead">Unfortunately, it looks like your password was wrong.</p>');
		for(i in jsonData.deauths) {
			if(jsonData.deauths[i] == SID.substring(0, 18)) {
				logText('Password was wrong. Added to deauths. Shame activated. You\'re bad and you should feel bad.');
				socket.send(JSON.stringify({'action':'shame','sid': SID}));
			}
		}
	}
}

function deauth() {
	logText('User has been deauthed.');
	$('.disabled').prop('disabled', true);
}