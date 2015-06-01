function auth() {
	for(i in jsonData.auths) {
		if(jsonData.auths[i] == SID.substring(0, 18)) {
			authed = true;
		}
	}

	if(authed) {
		logText("User has been authed. Displaying authed modal.");
		modalMessage('Success!', '<p class="lead">You\'ve been authorized!</p>');
	} else {
		modalMessage('Failure', '<p class="lead">Unfortunately, it looks like your password was wrong.</p>');
		for(i in jsonData.deauths) {
			if(jsonData.deauths[i] == SID.substring(0, 18)) {
				logText("Password was wrong. Added to deauths. Shame activated. You're bad and you should feel bad.");
				socket.send(JSON.stringify({"action":"shame","sid": SID}));
			}
		}
	}
}