// declare all globals here

var config, jsonData, socket, buttons,
	authed = false,
	queueEvents = {},
	allCuts = [],
	draggable = [],
	displayEl = {},
	formOptions = {},
	oldFormOptions = {"renderFormCalled": false},
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
			if (config.admin_mode_enabled && !authed) onAuth();
		}],
		"authfailed": [function deauthUser(data) {
			if (config.admin_mode_enabled && !authed) onFailedauth();
		}],
		"deauthed": [function userFailedAuth(data) {
			if(config.admin_mode_enabled && authed) onDeauth();
		}],
		"rickroll": [function rickRollUser(data) {
			NProgress.done();
			if(config.easter_eggs) rickRoll();
		}],
		"dodoododoooooo": [function dodoododoooooo(data) {
			NProgress.done();
			if(config.easter_eggs) johnCena();
		}],
		"refresh": [function refreshPage(data) {
			if(config.allow_force_refresh) window.location.reload();
		}],
		"notification": [function displayNotification(data) {
			modalMessage(data.title, data.text);
		}],
		"starttour": [function tourQueue(data) {
			if(config.allow_tour) queueTour();
		}]
	},
	renderDirectives = {
		priority: {
			html: function drawCoachMode(params) {
				return this.priority + (
					this.coachmodified ?
						' <span class="fa fa-cog coach-modified" data-toggle="tooltip" data-placement="bottom" title="{title}"></span>'.format({title: config.modified_hover})
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
						if (button != "pass" || !(params.index >= config.pass_depth && config.pass_depth || authed)) {
							data += buttons[button];
						}
					}
				}
				return data;
			},
		}
	};
