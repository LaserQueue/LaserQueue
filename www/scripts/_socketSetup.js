// a function to set up WebSockets

function socketSetup() { // god help me

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
				socket.send(JSON.stringify({"action": "null"}));
			}
		},refreshRate);
	};

	// when websockets message
	socket.onmessage = function(msg) {
		// print to log and consoles
		jsonData = JSON.parse($.parseJSON(msg.data));

		// if data is new
		if(JSON.stringify(jsonData) != JSON.stringify(oldJsonData)) {
			logText("new JSON received: " + JSON.stringify(jsonData, null, 2));

			$(jsonData["queue"]).each(function(index, el) {
				$(el).each(function(arrayIndex, arrayEl) {
					fullList = fullList.concat(arrayEl);
				});
			});



			$('.table-template').render(jsonData["queue"]);
					//if(arrayEl["coachmodified"]) { modifiedTag = ' <span class="glyphicon glyphicon-cog coach-modified" data-toggle="tooltip" data-placement="bottom" title="Coach-modified"></span>'; }
				// 	$('table.cutting-table tbody').append('
				// 		<tr>
				// 			<td class="col-md-1"></td>
				// 			<td class="col-md-2">' + arrayEl["name"] + '</td>
				// 			<td class="col-md-2">' + materials[arrayEl["material"]] + '</td>
				// 			<td class="col-md-1">' + arrayEl["esttime"] + ' minutes</td>
				// 			<td class="col-md-1">' + priorities[index] + modifiedTag + '</td>
				// 		</tr>
				// 	');
			// 	};
			// });

			populateActions();
		}
		oldJsonData = jsonData;
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

