// declare almost all globals here

var getConfigFile, config, host, jsonData, socket, buttons,
	authed = false,
	allCuts = [],
	draggable = [],
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
	displayEl = {},
	renderDirectives = {
		priority: {
			html: function drawCoachMode(params) {
				return this.priority + (
					this.coachmodified ?
						' <span class="glyphicon glyphicon-cog coach-modified" data-toggle="tooltip" data-placement="bottom" title="{0}"></span>'.format(config.modified_hover)
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
