// basically this handles everything WebSockets

NProgress.start();

function parseCut(arrayIndex, arrayEl) {
	// parse cut
	displayEl = $.extend({}, arrayEl); // deepcopy
	displayEl.material = config.materials[arrayEl.material];
	displayEl.priority = config.priorities[arrayEl.priority];
	var timetotal = arrayEl.esttime;
	var hours = Math.floor(timetotal / 60);
	timetotal -= hours * 60;
	var minutes = Math.floor(timetotal);
	timetotal -= minutes;
	var seconds = +(timetotal * 60).toFixed(2);

	var timeEstimate = String(hours ? hours + 'h' : '') + (minutes && hours ? ' ' : '');
	timeEstimate += String(minutes ? minutes + 'm' : '') + (seconds && minutes ? ' ' : '');
	timeEstimate += String(seconds ? seconds + 's' : '');

	displayEl.esttime = timeEstimate;

	// add to full list of cuts
	allCuts = allCuts.concat(displayEl);
}

function socketSetup() {

	// wait until host has a real value
	while (host === 'undefined') {}
	socket = new WebSocket(host);

	// when websockets connects
	socket.onopen = function handleSocketOpen() {
		// print to log and consoles
		onDeauth();
		logText('WebSockets connection opened successfully');

		$('#notify-modal').modal('hide');

		NProgress.done();
	};

	// when websockets message
	socket.onmessage = function handleMessage(msg) {

		// loads JSON data
		jsonData = JSON.parse(msg.data);

		// if data is new
		if (JSON.stringify(jsonData) !== JSON.stringify(oldJsonData) && 'action' in jsonData) {

			// deep copy jsonData to oldJsonData
			oldJsonData = $.extend({}, jsonData);

			// log the new data
			logText('new JSON received: {json}'.format({json: JSON.stringify(jsonData)}));

			// if being told to render table
			if (jsonData.action in acceptedAPIs) {
				for (var func in acceptedAPIs[jsonData.action]) {
					acceptedAPIs[jsonData.action][func](jsonData);
				}
			}
		}
	};
	// when websockets error
	socket.onerror = function handleWebSocketsError(error) {
		// go tell a nerd
		modalMessage('Error 4', 'Could not connect to socket at {host}. Maybe the backend is not running? This page will try to reconnect every few seconds. <br><br> <button class="btn btn-default btn-pink btn-retry">Retry</button>'.format({host: host}));

		// set up retry button
		$('.btn-retry').click(function reloadWithRandom() {
			window.location = "{origin}?foo={randnum}".format({
				origin: window.location.origin,
				randnum: Math.floor(Math.random() * 11000)
			});
		});
	};
}
