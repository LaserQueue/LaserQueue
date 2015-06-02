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
	},
	actions: {
		html: function(params) {
			return (
				authed ? '
				<i class="glyphicon glyphicon-chevron-up increment-job" data-toggle="tooltip" data-placement="right" title="Increment this job"></i>
				<i class="glyphicon glyphicon-chevron-down decrement-job" data-toggle="tooltip" data-placement="right" title="Decrement this job"></i>'
				: ''
			);
		},
	}
};

SID = uuid.v1();
window.console.log('I have SID ' + SID);

// fetches config file from server
getConfigFile = $.getJSON('/config.json', function() {

	config = getConfigFile.responseJSON;

	// hide and disable log if not enabled
	devLog = config.dev_log;
	if(devLog != true) { $('[for=log-checkbox]').slideUp(); }

	// log entire config file
	logText('Config file follows:' + JSON.stringify(getConfigFile.responseJSON, null, 2));

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
	for(var m in materials) {
		var selected = (m === config.default_material ? 'selected' : '');
		$('#cut-material').append('
			<option ' + selected + ' value="' + m + '" class="'+selected+'">' + materials[m] + '</option>
		');
	}

	// render the priorities dropdown
	for(var p in priorities) {
		var disabled = (p < config.default_priority && !config.priority_selection ? 'disabled ' : '');
		var selected = (p == config.default_priority ? 'selected' : '');
		$('#priority-dropdown').append('
			<option ' + selected + ' value="' + String(priorities.length-p-1) + '"  class="'+ disabled + selected + '">' + priorities[p] + '</option>
		');
	}

	if (!config.priority_selection) {
		$('.disabled').prop('disabled', true);
	}

	if(config.google_analytics_key == '') {
		logText('Google Analytics tracking is not enabled.');
	} else {
		logText('Google Analytics tracking is enabled with key ' + config.google_analytics_key);

		(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
		(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
		m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
		})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

		ga('create', config.google_analytics_key, {
			'cookieDomain': 'none'
		});

		ga('send', 'pageview');
	}

});