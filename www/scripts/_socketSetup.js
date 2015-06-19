// a function to set up WebSockets

function socketSetup() { // god help me

	// wait until host has a real value
	while(host == 'undefined') {}
	socket = new WebSocket(host);

	// when websockets connects
	socket.onopen = function() {
		// print to log and consoles
		logText('WebSockets connection opened successfully');

		$('#notify-modal').modal('hide');

		// poll for new data and repeat every refreshRate
		socketSend({'action': 'null'});
		setInterval(function () {
			if(socket.readyState != socket.CONNECTING) {
				socketSend({'action': 'null'});
			}
		},refreshRate);
	};

	// when websockets message
	socket.onmessage = function(msg) {

		// loads JSON data
		jsonData = JSON.parse(msg.data);

		// if data is new
		if(JSON.stringify(jsonData) !== JSON.stringify(oldJsonData)) {
		
			// deep copy jsonData to oldJsonData
			oldJsonData = $.extend({}, jsonData);
			
			// log the new data
			logText('new JSON received: ' + JSON.stringify(jsonData));

			// if being told to render table
			if(jsonData.action == 'display') {

				// reinitialize full list of cuts
				allCuts = [];

				if (config.admin_mode_enabled) {
					if (jsonData.auths.indexOf(SID.substring(0, 18)) < 0 && authed) {
						onDeauth();
					}
					else if (jsonData.auths.indexOf(SID.substring(0, 18)) >= 0 && !authed) {
						onAuth();
					}
					else if (jsonData.deauths.indexOf(SID.substring(0, 18)) >= 0 && !authed) {
						onFailedauth();
					}
				}
				// for each priority in list
				$(jsonData.queue).each(function(index, el) {

					// for each cut in priority
					$(el).each(function(arrayIndex, arrayEl) {
						// at this point nothing is human-readable
						// make material human-readable
						displayEl = $.extend({}, arrayEl); // deepcopy
						displayEl.material = materials[arrayEl.material];
						displayEl.priority = priorities[arrayEl.priority];
						var timetotal = arrayEl.esttime;
						var hours = Math.floor(timetotal/60);
						timetotal -= hours*60;
						var minutes = Math.floor(timetotal);
						timetotal -= minutes;
						var seconds = +(timetotal*60).toFixed(2);

						var output = String(hours ? hours+'h' : '') + (minutes && hours ? ' ' : '');
						output += String(minutes ? minutes+'m' : '') + (seconds && minutes ? ' ' : '');
						output += String(seconds ? seconds+'s' : '')

						displayEl.esttime = output;
						// add to full list of cuts
						allCuts = allCuts.concat(displayEl);
					});

				});
				
				// render allCuts into table
				$('.cutting-table-template').render(allCuts, renderDirectives);
				populateActions();
			}

		} else if(jsonData.action == 'rickroll') {
			rickRoll();
		} else if(jsonData.action == 'refresh' && config.allow_force_refresh) {
			window.location.reload();
		}
	};

	// when websockets error
	socket.onerror = function(error) {
		// go tell a nerd
		modalMessage('Error 4', 'Could not connect to socket at ' + host + '. Maybe the backend is not running? This page will try to reconnect every few seconds. <br><br> <button class="btn btn-default btn-pink btn-retry">Retry</button>');

		// set up retry button
		$('.btn-retry').click(function() {
			window.location = window.location.origin + '?foo=' + Math.floor(Math.random()*11000);
		});
	};
};

