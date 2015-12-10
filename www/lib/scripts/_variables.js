// declare all globals here

var config, jsonData, socket, buttons,
	extraData = {},
	authed = false,
	queueEvents = {},
	allCuts = [],
	draggable = [],
	displayEl = {},
	formOptions = {},
	oldFormOptions = {"renderFormCalled": false},
	commands = [],
	acceptedAPIs = {
		"display": [function displayData(data) {
			// reinitialize full list of cuts
			allCuts = [];
			// for each priority in list:
			for (var priority = data.queue.length; priority >= 0; priority--) {
				el = data.queue[priority];
				// for each cut in priority, render
				$(el).each(parseCut);
			}
			// render allCuts into table
			$('.jobs-table-template').render(allCuts, renderDirectives);
			populateActions();
		}],
		"job_added": [function endLoader() {
			logText("job_added received, so ending job addition loader");
			NProgress.done();
			$(queueEvents).trigger('add.succeed');
		}],
		"add_failed": [function endLoader() {
			logText("job_failed received, so ending job addition loader");
			NProgress.done();
			$(queueEvents).trigger('add.fail');
		}],
		"authed": [function authUser(data) {
			if (config.adminModeEnabled && !authed) onAuth();
		}],
		"auth_failed": [function deauthUser(data) {
			oldJsonData = {};
			if (config.adminModeEnabled && !authed) onFailedauth();
		}],
		"deauthed": [function userFailedAuth(data) {
			if(config.adminModeEnabled && authed) onDeauth();
		}],
		"egg": [function triggerEgg(data) {
			oldJsonData = {};
			NProgress.done();
			if(config.easterEggs) easterEggs[data.trigger]();
		}],
		"refresh": [function refreshPage(data) {
			if(config.allowForceRefresh) window.location.reload();
		}],
		"notification": [function displayNotification(data) {
			modalMessage(data.title, data.text);
		}],
		"start_tour": [function tourQueue(data) {
			oldJsonData = {};
			if(config.allowTour) queueTour();
		}],
		"dump_data": [function receiveData(data) {
			extraData[data.name] = JSON.parse(data.data);
		}],
		"log": [function logData(data) {
			logText(data.body);
		}]
	},
	easterEggs = {
		"rick": rickRoll,
		"cena": johnCena,
		"shia": justDoIt
	},
	renderDirectives = {
		priority: {
			html: function drawCoachMode(params) {
				return this.priority + (
					this.coachmodified ?
						' <span class="fa fa-cog coach-modified" data-toggle="tooltip" data-placement="bottom" title="{title}"></span>'.format({title: config.modifiedHover})
						: ''
				);
			},
		},
		actions: {
			html: function actionDirectiveHTML(params) {
				var data = '';
				for (var i = 0; i < Object.keys(buttons).length; i++) {
					var button = Object.keys(buttons)[i];
					if (config.authactions.indexOf(button) == -1 || authed) {
						if (button != "pass" || !(params.index >= config.passDepth && config.passDepth || authed)) {
							data += buttons[button];
						}
					}
				}
				return data;
			},
		}
	};
