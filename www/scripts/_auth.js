function onAuth() {
	authed = true;
	logText('Displaying authed modal.');
	modalMessage('Success!', '<p class="lead">You\'ve been authorized!</p>');
	setTimeout('
		$("#notify-modal").modal("hide");
	', 2000);
	$('.cutting-table-template').render(allCuts, renderDirectives);
	$('.disabled').prop('disabled', false);
	$('.authorize').attr('data-original-title', 'Click to log out');
}

function onFailedauth() {
	modalMessage('Failure', '<p class="lead">Unfortunately, it looks like your password was wrong.</p>');
	logText('Password was wrong. Added to deauths. Shame activated. You\'re bad and you should feel bad.');
	socketSend({'action':'shame'});
}

function onDeauth() {
	authed = false;
	logText('User has been deauthed.');
	$('.cutting-table-template').render(allCuts, renderDirectives);
	$('.disabled').prop('disabled', true);
	$('.authorize').attr('data-original-title', 'Click to authenticate');
}