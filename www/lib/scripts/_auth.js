// functions for auth

// set up admin mode if enabled
$(queueEvents).on('config.parsed', function() {
	if (config.adminModeEnabled) {
		$('.authorize').click(function handleAuthToggle() {
			// if already authorized, deauth
			if (authed) {
				socketSend({'action': 'deauth'});
				$('.authorize').tooltip('hide');
			} else {

				// if not authorized, present auth UI
				modalMessage('Authenticate',
					'<form class="login-form">' +
						'<div class="form-group">' +
							'<label for="password">Password</label>' +
							'<input type="password" class="form-control coach-password" id="password" placeholder="Password">' +
						'</div>' +
						'<button type="submit" class="btn btn-pink auth-button">Sign in</button>' +
					'</form>'
				);
				$('.authorize').tooltip('hide');

				// once modal is up, focus password
				setTimeout(function focusPasswordField() {
					$(".coach-password").focus();
				}, 500);

				// authenticate password when asked
				$('.auth-button').click(function authenticatePassword(event) {
					event.preventDefault();
					NProgress.start();
					if($('#password').val()) {
						logText('Password entered. Attempting auth.');
						socketSend({
							'action': 'auth',
							'pass': sha256($('#password').val())
						});
					}
				});
			}
		});
		$('.authorize').attr('data-original-title', config.login);
	}
});

// run on auth
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

// run on failed auth
function onFailedauth() {
	$(queueEvents).trigger('auth.failure');
	modalMessage('Failure', '<p class="lead">Unfortunately, it looks like your password was wrong.</p>');
	logText('Password was wrong. You\'re bad and you should feel bad.');
	NProgress.done();
}

// run on deauth
function onDeauth() {
	$(queueEvents).trigger('auth.deauth');
	authed = false;
	logText('User has been deauthed.');
	$('.jobs-table-template').render(allCuts, renderDirectives);
	$('.disabled').prop('disabled', true);
	$('.authorize').attr('data-original-title', config.login);
	$('.nuvu-logo').attr('src', '/dist/img/logo.svg');
	if (config.authactions.indexOf('relative_move') != -1) {
		$(draggable).draggabilly('disable');
	}
	if (config.authactions.indexOf('add') != -1) {
		$('.job-form-group').hide();
	}
	populateActions();
	renderForm();
}
