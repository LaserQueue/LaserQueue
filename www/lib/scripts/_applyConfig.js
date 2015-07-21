// gets the config file, parses and applies values
getConfigFile = $.getJSON('/config.json', function getConfigFileFunction() {

	// config.thing returns thing in the config file
	config = getConfigFile.responseJSON;

	// hide and disable log if not enabled
	devLog = config.dev_log;

	if(!devLog) {
		$('[for=log-checkbox]').remove();
	} else {
		console.log('Recommended: use the in-page log. Most info goes there.');
	}

	logText('Begin log');

	// log entire config file
	logText('Config file follows: {0}'.format(JSON.stringify(config, null, 2)));

	// set WebSockets hostname and port from config
	host = 'ws://{0}:{1}'.format(config.host, config.port);

	// set page title
	if (config.page_title) {
		$('title').text(config.page_title);
	}

	// set materials and priorities from config
	materials = config.materials;
	priorities = config.priorities;

	// set refreshRate and reconnectRate from config
	refreshRate = config.refreshRate;
	reconnectRate = config.reconnectRate;

	// take easter eggs boolean from config
	easterEggs = config.easter_eggs;

	// hide task add form if auth is required to add
	addEnabled = (config.authactions.indexOf('add') == -1);
	if (!addEnabled) {
		$('.job-form-group').hide();
	}

	// render materials dropdown
	if (!config.default_material) {
		$('#job-material').append('<option disabled selected value="N/A" class="selected">{0}</option>'.format(config.material_input));
	}
	for(var m in materials) {
		var mat_selected = (m === config.default_material ? 'selected' : '');
		$('#job-material').append('<option {0} value="{1}" class="{0}">{2}</option>'.format(
			mat_selected, m, materials[m]));
	}

	// render the priorities dropdown
	if (config.priority_choose) {
		$('#job-priority').append('<option disabled selected value="-1" class="selected">{0}</option>'.format(config.priority_input));
	}
	for(var p in priorities) {
		var disabled = (p < config.default_priority && !config.priority_selection ? 'disabled' : '');
		var pri_selected = (p == config.default_priority && !config.priority_choose ? 'selected' : '');
		$('#job-priority').append('<option {0} value="{1}"  class="{2} {0}">{3}</option>'.format(
			pri_selected, String(priorities.length-p-1), disabled, priorities[p]));
	}
	if (!config.priority_selection) {
		$('.disabled').prop('disabled', true);
	}

	// set textbox placeholders from config
	$('.job-human-name').attr('placeholder', config.name_input);
	$('.job-time-estimate').attr('placeholder', config.time_input);

	// set tooltips from config
	$('.job-human-name').attr('title', config.name_hover);
	$('.job-time-estimate').attr('title', config.time_hover);
	$('.job-material').attr('title', config.material_hover);
	$('.job-priority').attr('title', config.priority_hover);

	// set table headers from config
	$('.action-header').text(config.action_header);
	$('.name-header').text(config.name_header);
	$('.material-header').text(config.material_header);
	$('.time-header').text(config.time_header);
	$('.priority-header').text(config.priority_header);

	// set up action buttons from config
	buttons = {
		'remove': '\n<a role="button" tabindex="0" class="glyphicon glyphicon-remove remove-job" data-toggle="tooltip" data-placement="right" title="{0}"></a>'.format(config.remove_hover),
		'increment': '\n<a role="button" tabindex="0" class="glyphicon glyphicon-chevron-up increment-job" data-toggle="tooltip" data-placement="right" title="{0}"></a>'.format(config.incr_hover),
		'decrement': '\n<a role="button" tabindex="0" class="glyphicon glyphicon-chevron-down decrement-job" data-toggle="tooltip" data-placement="right" title="{0}"></a>'.format(config.decr_hover),
		'pass': '\n<a role="button" tabindex="0" class="glyphicon glyphicon-triangle-bottom lower-priority" data-toggle="tooltip" data-placement="right" title="{0}"></a>'.format(config.pass_hover),
		'relmove': '\n<a role="button" tabindex="0" class="glyphicon glyphicon-menu-hamburger move-job" data-toggle="tooltip" data-placement="right" title="{0}"></a>'.format(config.drag_hover)
	};

	// set up admin mode if enabled
	if (config.admin_mode_enabled) {
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
						'<button type="submit" class="btn btn-default auth-button">Sign in</button>' +
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

	// enable Google Analytics if config says so
	if(!config.google_analytics_key) {
		logText('Google Analytics tracking is not enabled.');
	} else {
		logText('Google Analytics tracking is enabled with key ' + config.google_analytics_key);

		/* jshint ignore:start */
		(function GAisogram(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function googleAnalyticsFunction(){
		(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
			m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
		})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
		/* jshint ignore:end */

		googleAnalytics('create', config.google_analytics_key, {
			'cookieDomain': 'none'
		});
		googleAnalytics('send', 'pageview');
	}

	// log status
	logText('LaserQueue is up and config is loaded and parsed. Attempting connection to WebSockets host at {0}.'.format(host));

	// attempt WebSockets connection
	socketSetup();

	// maintain connection if dropped
	setInterval(function tryToReconnect() {
		if(typeof reconnectRate != 'undefined' && (typeof socket == 'undefined' || socket.readyState == socket.CLOSED)) {
			// initialize websockets if closed
			logText('Attempting connection to WebSockets host {0}.'.format(host));
			socketSetup();
		}
	}, reconnectRate);

});