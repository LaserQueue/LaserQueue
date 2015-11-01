// gets the config file, parses and applies values

var getConfigFile = $.getJSON('/config.json', function getConfigFileFunction() {
	// config.thing returns thing in the config file
	config = getConfigFile.responseJSON;

	if(!config.devLog) {
		$('[for=log-checkbox]').remove();
	} else {
		console.log('Recommended: use the in-page log. Most info goes there.');
	}

	logText('Begin log');

	// log entire config file
	logText('Config file follows: {config}'.format({config: JSON.stringify(config, null, 2)}));

	// set WebSockets hostname and port from config
	host = 'ws://{host}:{port}'.format({host: config.host, port: config.port});

	// set page title
	if (config.pageTitle) {
		$('title').text(config.pageTitle);
	}

	// hide task add form if auth is required to add
	if (config.authactions.indexOf('add') != -1) {
		$('.job-form-group').hide();
	}

	// set up form options
	formOptions = {
		"name": {
			"type": "string",
			"placeholder": config.nameInput,
			"tooltip": config.nameHover,
			"classes": ["job-human-name"]
		},
		"time": {
			"type": "string",
			"placeholder": config.timeInput,
			"tooltip": config.timeHover,
			"classes": ["job-time-estimate"]
		},
		"material": {
			"type": "select",
			"tooltip": config.materialHover,
			"header": config.materialInput,
			"options": config.materials,
			"classes": ["job-material"]
		},
		"priority": {
			"type": "select",
			"tooltip": config.priorityHover,
			"header": config.priorityInput,
			"options": config.priorities,
			"classes": ["job-priority"]
		}
	};

	// render the form
	renderForm();

	// set table headers from config
	$('.action-header').text(config.actionHeader);
	$('.name-header').text(config.nameHeader);
	$('.material-header').text(config.materialHeader);
	$('.time-header').text(config.timeHeader);
	$('.priority-header').text(config.priorityHeader);

	// set up action buttons from config
	buttons = {
		'remove': '\n<a role="button" tabindex="0" class="fa fa-remove remove-job" data-toggle="tooltip" data-placement="right" title="{title}"></a>'.format({title: config.removeHover}),
		'increment': '\n<a role="button" tabindex="0" class="fa fa-chevron-up increment-job" data-toggle="tooltip" data-placement="right" title="{title}"></a>'.format({title: config.incrHover}),
		'decrement': '\n<a role="button" tabindex="0" class="fa fa-chevron-down decrement-job" data-toggle="tooltip" data-placement="right" title="{title}"></a>'.format({title: config.decrHover}),
		'pass': '\n<a role="button" tabindex="0" class="fa fa-chevron-down lower-priority" data-toggle="tooltip" data-placement="right" title="{title}"></a>'.format({title: config.passHover}),
		'relmove': '\n<a role="button" tabindex="0" class="fa fa-bars move-job" data-toggle="tooltip" data-placement="right" title="{title}"></a>'.format({title: config.dragHover})
	};

	// set up admin mode if enabled
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

	// enable Google Analytics if config says so
	if(!config.googleAnalyticsKey) {
		logText('Google Analytics tracking is not enabled.');
	} else {
		logText('Google Analytics tracking is enabled with key ' + config.googleAnalyticsKey);

		/* jshint ignore:start */
		(function GAisogram(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function googleAnalyticsFunction(){
		(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
			m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
		})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
		/* jshint ignore:end */

		googleAnalytics('create', config.googleAnalyticsKey, {
			'cookieDomain': 'none'
		});
		googleAnalytics('send', 'pageview');
	}

	// log status
	logText('LaserQueue {version} is up and config is loaded and parsed. Attempting connection to WebSockets host at {host}.'.format({version: config.version,host: host}));

	// attempt WebSockets connection
	socketSetup();

	// maintain connection if dropped
	setInterval(function tryToReconnect() {
		if(typeof config.reconnectRate != 'undefined' && (typeof socket == 'undefined' || socket.readyState == socket.CLOSED)) {
			// initialize websockets if closed
			logText('Attempting connection to WebSockets host {host}.'.format({host: host}));
			socketSetup();
		}
	}, config.reconnectRate);

	$(queueEvents).trigger('config.parsed');

});
