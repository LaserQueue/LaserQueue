function auth() {
	authed = true;
	logText('Displaying authed modal.');
	modalMessage('Success!', '<p class="lead">You\'ve been authorized!</p>');
	$('.cutting-table-template').render(allCuts, renderDirectives);
	$('.disabled').prop('disabled', false);
}

function failedauth() {
	modalMessage('Failure', '<p class="lead">Unfortunately, it looks like your password was wrong.</p>');
	logText('Password was wrong. Added to deauths. Shame activated. You\'re bad and you should feel bad.');
	socketSend({'action':'shame'});
}

function deauth() {
	authed = false;
	logText('User has been deauthed.');
	$('.disabled').prop('disabled', true);
}