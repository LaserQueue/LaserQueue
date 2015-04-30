function socketSetup() { // god help me

	socket = new WebSocket(host);

	// when websockets connects
	socket.onopen = function() {
		// print to log and consoles
		window.console.log("Socket has been opened!");
		logText('WebSockets connection opened successfully \n');

		socket.send(JSON.stringify({"action": "null"}));
		setInterval(function () {
			socket.send(JSON.stringify({"action": "null"}));
		},refreshRate);
	};

	// when websockets message
	socket.onmessage = function(msg){
		// print to log and consoles
		var jsonData = JSON.parse($.parseJSON(msg.data));

		// if data is new
		if(JSON.stringify(jsonData) != JSON.stringify(oldJsonData)) {
			
			logText("old JSON: " + JSON.stringify(oldJsonData));
			logText("new JSON received: " + JSON.stringify(jsonData));
			$('table.cutting-table tbody').html(tableFirstRow);
			$(jsonData["queue"]).each(function(index, el) {
				$(el).each(function(arrayIndex, arrayEl) {
					var modifiedTag = "";
					if(arrayEl["coachmodified"]) { modifiedTag = ' <span class="glyphicon glyphicon-cog coach-modified" data-toggle="tooltip" data-placement="bottom" title="Coach-modified"></span>'; }
					$('table.cutting-table tbody').append('
						<tr>
							<td class="col-md-1"></td>
							<td class="col-md-2">' + arrayEl["name"] + '</td>
							<td class="col-md-2">' + materials[arrayEl["material"]] + '</td>
							<td class="col-md-1">' + arrayEl["esttime"] + ' minutes</td>
							<td class="col-md-1">' + priorities[index] + modifiedTag + '</td>
						</tr>
					');
				});
			});
			populateActions();
		}
		oldJsonData = jsonData;
	};

	// when websockets error
	socket.onerror = function(error) {
		// go tell a nerd
		modalMessage("Error 4", "Could not connect to socket at " + host + ". Maybe the backend is not running?");
	};
};

