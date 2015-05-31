// gets the config file and parses values

// declare almost all globals here
var getConfigFile, config, host, jsonData, socket, materials, priorities,  refreshRate, reconnectRate, easterEggs, SID;
var authed = false;
var allCuts = [];
var displayEl = {}
var renderDirectives = {
	priority: {
		html: function(params) {
			return this.priority + (
				this.coachmodified ? 
					' <span class="glyphicon glyphicon-cog coach-modified" data-toggle="tooltip" data-placement="bottom" title="' + getConfigFile.responseJSON['modified_hover'] + '"></span>'
					: ''
			);
		},
	}
};

SID = uuid.v1();
window.console.log("I have SID " + SID);

// fetches config file from server
getConfigFile = $.getJSON('/config.json', function() {

	config = getConfigFile.responseJSON;

	// hide and disable log if not enabled
	devLog = getConfigFile.responseJSON["dev_log"];
	if(devLog != true) { $('[for=log-checkbox]').slideUp(); }

	// log entire config file
	logText("Config file follows:" + JSON.stringify(getConfigFile.responseJSON, null, 2));

	// set host from host and port
	host = "ws://" + getConfigFile.responseJSON["host"] + ":" + getConfigFile.responseJSON["port"];

	// set materials and priorities in the same way
	materials = getConfigFile.responseJSON["materials"];
	priorities = getConfigFile.responseJSON["priorities"];

	// set refreshRate and reconnectRate
	refreshRate = getConfigFile.responseJSON["refreshRate"];
	reconnectRate = getConfigFile.responseJSON["reconnectRate"];

	easterEggs = getConfigFile.responseJSON["easter_eggs"];

	// render the materials dropdown
	for(var m in materials) {
		$('#cut-material').append('
			<option ' + (m === config.default_material ? 'selected' : '' ) + ' value="' + m + '">' + materials[m] + '</option>
		');
	}

	// render the priorities dropdown
	for(var p in priorities) {
		$('#priority-dropdown').append('
			<option ' + (p == config.default_priority ? 'selected' : '') + ' value="' + String(priorities.length-p-1) + '">' + priorities[p] + '</option>
		');
	}

	if(config.google_analytics_key == '') {
		logText("Google Analytics tracking is not enabled.");
	} else {
		logText("Google Analytics tracking is enabled with key " + +config.google_analytics_key);
		$('body').append("
			<script>
				(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
				(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
				m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
				})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

				ga('create', '" + config.google_analytics_key + "', {
					'cookieDomain': 'none'
				});
				ga('set', 'forceSSL', true);
				ga('send', 'pageview');

			</script>
		");
	}

});