// a function to set up WebSockets

function socketSetup() { // god help me

	// wait until host has a real value
	while(host == 'undefined') {}
	socket = new WebSocket(host);

	// when websockets connects
	socket.onopen = function() {
		// print to log and consoles
		logText('WebSockets connection opened successfully \n');

		$('#notify-modal').modal('hide');

		// poll for new data and repeat every refreshRate
		socket.send(JSON.stringify({"action": "null"}));
		setInterval(function () {
			if(socket.readyState != socket.CONNECTING) {
				socket.send(JSON.stringify({
					"action": "null",
					"sid": SID
				}));
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
			if(jsonData.action == "display") {

				// reinitialize full list of cuts
				allCuts = [];

				if (jsonData.auths.indexOf(SID.substring(0, 18)) <= 0) {
					deauth();
				}

				// for each priority in list
				$(jsonData["queue"]).each(function(index, el) {

					// for each cut in priority
					$(el).each(function(arrayIndex, arrayEl) {
						// at this point nothing is human-readable
						// make material human-readable
						displayEl = $.extend({}, arrayEl); // deepcopy
						displayEl.material = materials[arrayEl.material];
						displayEl.priority = priorities[arrayEl.priority];
						displayEl.esttime = arrayEl.esttime + (arrayEl.esttime == 1 ? ' minute' : ' minutes');
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
		}
	};

	// when websockets error
	socket.onerror = function(error) {
		// go tell a nerd
		modalMessage("Error 4", "Could not connect to socket at " + host + ". Maybe the backend is not running? This page will try to reconnect every few seconds. <br><br> <button class='btn btn-default btn-pink btn-retry'>Retry</button>");

		// set up retry button
		$('.btn-retry').click(function() {
			window.location = window.location.origin + "?foo=" + Math.floor(Math.random()*11000);
		});
	};
};

