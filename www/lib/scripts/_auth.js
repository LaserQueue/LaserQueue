// functions for auth

'use strict';

function onAuth() {
	authed = true;
	logText('Displaying authed modal.');
	modalMessage('Success!', '<p class="lead">You\'ve been authorized!</p>');
	setTimeout(function hideModal() {
		$("#notify-modal").modal("hide");
	}, 1000);
	$('.jobs-table-template').render(allCuts, renderDirectives);
	$('.disabled').prop('disabled', false);
	$('.authorize').attr('data-original-title', config.logout);
	$('.nuvu-logo').attr('src', '/dist/img/admin-logo.svg');
	if (!addEnabled) {
		$('.job-form-group').show();
	}
	populateActions();
}

function onFailedauth() {
	modalMessage('Failure', '<p class="lead">Unfortunately, it looks like your password was wrong.</p>');
	logText('Password was wrong. You\'re bad and you should feel bad.');
}

function onDeauth() {
	authed = false;
	logText('User has been deauthed.');
	$('.jobs-table-template').render(allCuts, renderDirectives);
	$('.disabled').prop('disabled', true);
	$('.authorize').attr('data-original-title', config.login);
	$('.nuvu-logo').attr('src', '/dist/img/logo.svg');
	if (config.authactions.indexOf('relmove') != -1) {
		$(draggable).draggabilly('disable');
	}
	if (!addEnabled) {
		$('.job-form-group').hide();
	}
	populateActions();
}
