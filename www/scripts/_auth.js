function auth() {
	for(i in jsonData.auths) {
		if(jsonData.auths[i] == SID.substring(0, 18)) {
			authed = true;
		}
	}

	if(authed) {
		modalMessage('Success!', '<p class="lead">You\'ve been authorized!</p>');
	}
}

function deauth() {

}