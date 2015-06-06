// gets the config file and parses values

// declare almost all globals here
var getConfigFile, config, host, jsonData, socket, materials, priorities,  refreshRate, reconnectRate, easterEggs, SID,
    authed = false,
    allCuts = [],
    displayEl = {},
    renderDirectives = {
	priority: {
		html: function(params) {
			return this.priority + (
				this.coachmodified ? 
					' <span class="glyphicon glyphicon-cog coach-modified" data-toggle="tooltip" data-placement="bottom" title="' + config.modified_hover + '"></span>'
					: ''
			);
		},
	},
	actions: {
		html: function(params) {
			return (
				authed ? '
				<i class="glyphicon glyphicon-remove remove-job" data-toggle="tooltip" data-placement="right" title="' + config.remove_hover + '"></i>
				<i class="glyphicon glyphicon-chevron-up increment-job" data-toggle="tooltip" data-placement="right" title="' + config.incr_hover + '"></i> 
				<i class="glyphicon glyphicon-chevron-down decrement-job" data-toggle="tooltip" data-placement="right" title="' + config.decr_hover + '"></i>'
				: params.index >= config.pass_depth && config.pass_depth ? '
				<i class="glyphicon glyphicon-remove remove-job" data-toggle="tooltip" data-placement="right" title="' + config.remove_hover + '"></i>'
				:  '
				<i class="glyphicon glyphicon-remove remove-job" data-toggle="tooltip" data-placement="right" title="' + config.remove_hover + '"></i>
				<i class="glyphicon glyphicon-triangle-bottom lower-priority" data-toggle="tooltip" data-placement="right" title="' + config.pass_hover + '"></i>'
			);
		},
	}
};

// generate a session ID
SID = uuid.v1();
window.console.log('SID: ' + SID);

// fetches config file from server
getConfigFile = $.getJSON('/config.json', function() {

	// config.thing returns thing in the config file
	config = getConfigFile.responseJSON;

	// hide and disable log if not enabled
	devLog = config.dev_log;
	if(devLog != true) { $('[for=log-checkbox]').slideUp(); }
	logText('Log starts here');

	// log entire config file
	logText('Config file follows: ' + JSON.stringify(config, null, 2));

	// set host from host and port
	host = 'ws://' + config.host + ':' + config.port;

	// set materials and priorities in the same way
	materials = config.materials;
	priorities = config.priorities;

	// set refreshRate and reconnectRate
	refreshRate = config.refreshRate;
	reconnectRate = config.reconnectRate;

	easterEggs = config.easter_eggs;

	// render the materials dropdown
	if (config.default_material == "") {
		$('#cut-material').append('
			<option disabled selected value="N/A" class="selected">' + config.material_input + '</option>
		');
	}
	for(var m in materials) {
		var selected = (m === config.default_material ? 'selected' : '');
		$('#cut-material').append('
			<option ' + selected + ' value="' + m + '" class="'+selected+'">' + materials[m] + '</option>
		');
	}

	// render the priorities dropdown
	if (config.priority_choose) {
		$('#priority-dropdown').append('
			<option disabled selected value="-1" class="selected">' + config.priority_input + '</option>
		');
	}
	for(var p in priorities) {
		var disabled = (p < config.default_priority && !config.priority_selection ? 'disabled ' : '');
		var selected = (p == config.default_priority && !config.priority_choose ? 'selected' : '');
		$('#priority-dropdown').append('
			<option ' + selected + ' value="' + String(priorities.length-p-1) + '"  class="'+ disabled + selected + '">' + priorities[p] + '</option>
		');
	}

	if (!config.priority_selection) {
		$('.disabled').prop('disabled', true);
	}

	$('.cut-human-name').attr('placeholder', config.name_input);
	$('.cut-time-estimate').attr('placeholder', config.time_input);
	$('.cut-human-name').attr('title', config.name_hover);
	$('.cut-time-estimate').attr('title', config.time_hover);
	$('.cut-material').attr('title', config.material_hover);
	$('.priority-dropdown').attr('title', config.priority_hover);

	if (config.admin_mode_enabled) {
		$('.authorize').click(function() {
			if (authed) {
				socketSend({'action': 'deauth'});
				$('.authorize').tooltip('hide');
			}
			else {
				modalMessage('Authenticate', '
					<form class="login-form">
						<div class="form-group">
							<label for="password">Password</label>
							<input type="password" class="form-control coach-password" id="password" placeholder="Password">
						</div>
						<button type="submit" class="btn btn-default">Sign in</button>
					</form>
				');
				$('.authorize').tooltip('hide');

				setTimeout('
					$(".coach-password").focus();
				',500);

				

				$('.login-form').submit(function(event) {
					event.preventDefault();
					if($('#password').val() != '') {
						logText('Password entered. Attempting auth.');
						socketSend({
							'action': 'auth',
							'args': [sha1($('#password').val())]
						});
						
					}
				});
			}
		});
		$('.authorize').attr('data-original-title', config.login);
	};

	if(config.google_analytics_key == '') {
		logText('Google Analytics tracking is not enabled.');
	} else {
		logText('Google Analytics tracking is enabled with key ' + config.google_analytics_key);

		(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
		(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
		m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
		})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

		googleAnalytics('create', config.google_analytics_key, {
			'cookieDomain': 'none'
		});

		googleAnalytics('send', 'pageview');
	}

	logText('LaserCutter software is up. Attempting connection to WebSockets host ' + host);
	socketSetup();
	setInterval(function() {
		if(typeof reconnectRate != 'undefined' && (typeof socket == 'undefined' || socket.readyState == socket.CLOSED)) {
			// initialize websockets if closed
			logText('Attempting connection to WebSockets host', host);
			socketSetup();
		}
	}, reconnectRate);

});