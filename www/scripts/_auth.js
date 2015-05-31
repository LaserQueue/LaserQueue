function auth() {
	for(i in jsonData.auths) {
		if(jsonData.auths[i] == SID.substring(0, 18)) {
			authed = true;
		}
	}

	if(authed) {
		modalMessage('Success!', '<p class="lead">You\'ve been authorized!</p>');
	} else {
		modalMessage('Failure', '<p class="lead">Unfortunately, it looks like your password was wrong.</p>');
		for(i in jsonData.deauths) {
			if(jsonData.deauths[i] == SID.substring(0, 18)) {
				socket.send(JSON.stringify({"action":"shame","sid": SID}));
			}
		}
	}
}