// functions for auth

function onAuth() {
	$(queueEvents).trigger('auth.success');
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
	if (config.authactions.indexOf('add') != -1) {
		$('.job-form-group').show();
	}
	populateActions();
	renderForm();
	NProgress.done();
}

function onFailedauth() {
	$(queueEvents).trigger('auth.failure');
	modalMessage('Failure', '<p class="lead">Unfortunately, it looks like your password was wrong.</p>');
	logText('Password was wrong. You\'re bad and you should feel bad.');
	NProgress.done();
}

function onDeauth() {
	$(queueEvents).trigger('auth.deauth');
	authed = false;
	logText('User has been deauthed.');
	$('.jobs-table-template').render(allCuts, renderDirectives);
	$('.disabled').prop('disabled', true);
	$('.authorize').attr('data-original-title', config.login);
	$('.nuvu-logo').attr('src', '/dist/img/logo.svg');
	if (config.authactions.indexOf('relmove') != -1) {
		$(draggable).draggabilly('disable');
	}
	if (config.authactions.indexOf('add') != -1) {
		$('.job-form-group').hide();
	}
	populateActions();
	renderForm();
}
