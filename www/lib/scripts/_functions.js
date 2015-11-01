// utilities and functions etc

String.prototype.format = function formatString() {
	var str = this.toString();
	if (!arguments.length)
		return str;
	var args = typeof arguments[0];
	args = (("string" == args || "number" == args) ? arguments : arguments[0]);
	for (var arg in args)
		str = str.replace(RegExp("\\{" + arg + "\\}", "gi"), args[arg]);
	return str;
};


if (!String.prototype.repeat) {
	String.prototype.repeat = function countThrough(count) {
		'use strict';
		if (this === null) {
			throw new TypeError('can\'t convert {object} to object'.format({object: this}));
		}
		var str = '' + this;
		count = +count;
		if (count != count) {
			count = 0;
		}
		if (count < 0) {
			return str;
		}
		if (count == Infinity) {
			throw new RangeError('repeat count must be less than infinity');
		}
		count = Math.floor(count);
		if (str.length === 0 || count === 0) {
			return '';
		}
		// ensuring count is a 31-bit integer allows us to heavily optimize the
		// main part. But anyway, most current (August 2014) browsers can't handle
		// strings 1 << 28 chars or longer, so:
		if (str.length * count >= 1 << 28) {
			throw new RangeError('repeat count must not overflow maximum string size');
		}
		var rpt = '';
		for (;;) {
			if ((count & 1) == 1) {
				rpt += str;
			}
			count >>>= 1;
			if (count === 0) {
				break;
			}
			str += str;
		}
		return rpt;
	};
}

function splatArgs(func, args) {
	return Array.prototype.slice.call(args, func.length);
}


function ensureNumberStringLength(number, len) {
	return '0'.repeat(len - String(number).length) + String(number);
}

// logs text to devlog on page
function logText(text) {
	if(config.devLog) {
		var currentTime = new Date();
		var currentDay = ensureNumberStringLength(currentTime.getDate(), 2);
		var currentMonth = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][currentTime.getMonth()];
		var currentYear = currentTime.getFullYear();
		var currentHours = ensureNumberStringLength(currentTime.getHours(), 2);
		var currentMinutes = ensureNumberStringLength(currentTime.getMinutes(), 2);
		var currentSeconds = ensureNumberStringLength(currentTime.getSeconds(), 2);

		var timestamp = ' [{dd}/{month}/{yyyy} {hh}:{mm}:{ss}] '.format({
			dd: currentDay, month: currentMonth, yyyy: currentYear,
			hh: currentHours, mm: currentMinutes, ss: currentSeconds
		});

		var textArray = text.split('\n');

		for (var i = textArray.length - 1; i > 0; i--) {
			$('.log-pre').prepend('<span class="log-time">{whitespace}</span>{text}\n'.format({
				whitespace: ' '.repeat(24),
				text: textArray[i]}));
		}
		$('.log-pre').prepend('<span class="log-time">{stamp}</span>{text}\n'.format({
			stamp: timestamp,
			text: textArray[0]}));
	} else {
		window.console.log(text);
	}
}

// initialize tooltips
function tooltips() {
	$('[data-toggle="tooltip"]').tooltip({trigger: 'hover'});
}

// repopulate action button UUIDs
function populateActions() {
	logText('Populating actions');

	$('.jobs-table-template tr').each(function dataToTable(index, el) {
		$(el).attr('data-uuid', allCuts[index].uuid);
		$(el).attr('data-pos', index);
		$(el).unbind('click');
	});

	// reinitialize bootstrap tooltips
	if(isTouchDevice() === false) {
		tooltips();
	}

	$('.action-box a').mousedown(function hideTooltips() {
		$(this).tooltip('hide');
	});

	// handler to remove a job
	$('.remove-job').click(function handleRemove(event) {
		// remove job based on action button
		var uuidToRemove = $(this).parents('[data-uuid]')[0].dataset.uuid;
		var removeJob = function removeJob(actionButton) {
			googleAnalytics('send', 'event', 'action', 'click', 'remove job');
			logText('removing item {uuid}'.format({uuid: $($(this).parents()[1]).attr('data-uuid')}));
			socketSend({
				'action': 'remove',
				'uuid': uuidToRemove
			});
		};
		if(event.altKey) {
			removeJob(this);
		} else {
			$(event.target).tooltip('hide');
			$('.remove-job').popover('hide');
			$(event.target).popover({
				placement: 'bottom',
				html: true,
				content: function confirmModalContents() {
					return '<button class="btn btn-default btn-secondary btn-lg btn-block cancel-remove">No</button>' +
						'<button class="btn btn-danger btn-lg btn-block confirm-remove">Yes</button>';
				}
			});
			$(event.target).popover('show');
			$('.confirm-remove').focus();
			$('.cancel-remove').click(function cancelRemove(event) {
				$('.remove-job').popover('hide');
			});
			$('.confirm-remove').click(function confirmRemove(event) {
				removeJob(this);
				$('.remove-job').popover('hide');
			});
		}
	});

	// handler to lower a job
	$('.lower-priority').click(function lowerPriority() {
		googleAnalytics('send', 'event', 'action', 'click', 'pass job');
		logText('passing item {uuid}'.format({uuid: $($(this).parents()[1]).attr('data-uuid')}));
		socketSend({
			'action': 'pass',
			'uuid': $($(this).parents()[1]).attr('data-uuid')
		});
	});

	// handler to decrement a job
	$('.decrement-job').click(function decrementJob() {
		googleAnalytics('send', 'event', 'action', 'click', 'decrement job');
		logText('removing item {uuid}'.format({uuid: $($(this).parents()[1]).attr('data-uuid')}));
		socketSend({
			'action': 'decrement',
			'uuid': $($(this).parents()[1]).attr('data-uuid')
		});
	});

	// handler to increment a job
	$('.increment-job').click(function incrementJob() {
		googleAnalytics('send', 'event', 'action', 'click', 'increment job');
		logText('passing item {uuid}'.format({uuid: $($(this).parents()[1]).attr('data-uuid')}));
		socketSend({
			'action': 'increment',
			'uuid': $($(this).parents()[1]).attr('data-uuid')
		});
	});

	if (authed || config.authactions.indexOf('relmove') == -1) {
		$('.jobs-table-template tr').each(function makeRowsDraggable(index, el) {
			draggable[index] = this;
			$(this).draggabilly({
				axis: 'y',
				container: $('.jobs-table-template')//,
				// grid: [ 37, 37 ]
			});
			$(this).on('dragStart', function handleDragStart() {
				$('[data-toggle="tooltip"]').tooltip('hide');
				$('.jobs-table-template tr:not(.is-dragging) td:nth-child(1) a.fa').addClass('animate-hide');
			});
			$(this).on('dragEnd', function handleDragEnd(event, pointer) {
				$('.jobs-table-template tr:not(.is-dragging) td:nth-child(1) a.fa').removeClass('animate-hide');
				socketSend({
					'action': 'relmove',
					'uuid': $(this).attr('data-uuid'),
					'targetIndex': parseInt($(this).attr('data-pos')) + parseInt(Math.round($(this).data('draggabilly').position.y / $(this).height()))
				});
			});
		});
	}
	$(queueEvents).trigger('actions.populated');
}

// displays message in a bootstrap modal
function modalMessage(modalTitle, modalBody, dialogOptions) {
	// hide all dialogs up
	bootbox.hideAll();

	// the object to pass to bootbox
	var dialogObj = {
		title: modalTitle,
		message: modalBody
	};

	// include all modal options
	if (typeof dialogOptions !== 'undefined') {
		dialogObj = $.extend(dialogObj, dialogOptions);
	}

	// show the dialog with message and title
	bootbox.dialog(dialogObj);

	// insert the hooks we want
	$('.bootbox').attr('id', 'notify-modal');
	$('.modal-title').addClass('notify-modal-title');
	$('.modal-title').attr('id', 'notify-modal-label');
	$('.modal-body').addClass('notify-modal-body');

	// bind clicking background to hiding modal
	$('.bootbox').click(function bgClickHideModals(event) {
		if (event.target.id === 'notify-modal') {
			bootbox.hideAll();
		}
	});
}

// reset a form with thanks to http://stackoverflow.com/questions/680241/resetting-a-multi-stage-form-with-jquery
function resetForm(form) {
	form.find('input:text, input:password, input[type=number], input:file, textarea').val(''); // removed 'select'
	form.find('input:radio, input:checkbox').removeAttr('checked').removeAttr('selected');
	if($(form).selector == '.new-job-form') {
		form.find('.selected').prop('selected', true);
	}
	$(queueEvents).trigger('form.reset');
}

// sends over websockets if the connection is stable
function socketSend(jdata) {
	var socketState = socket.readyState;
	if(socketState == 1) {
		socket.send(JSON.stringify(jdata));
	} else {
		// if not sending, log why
		if(socket.readyState != 1) {
			logText('socketSend() has been called, but socket.readyState is {state}. The socket is probably not connected yet.'.format({state: socketState}));
		}
	}
}

// render the job submission form
function renderForm() {
	$(queueEvents).trigger('form.render');
	if(formOptions === {}) {
		logText('renderForm() called but formOptions is blank. Not rendering.');
	} else if(JSON.stringify(formOptions) === JSON.stringify(oldFormOptions)) {
		logText('renderForm() called but formOptions match cached old formOptions. Not rendering.');
	} else {
		logText('rendering form');

		// cache form elements
		$('.form-group > *:not(.btn-submit)').each(function cacheFormElements() {
			if (formOptions[$(this).data('formEl')]) {
				formOptions[$(this).data('formEl')].cachedVal = $(this).val();
			}
		});

		// clear the form group aside from submit button
		$('.job-form-group').html('<button type="submit" class="btn btn-default btn-pink btn-submit">Submit</button>');

		// for each form option
		for(var i in formOptions) {
			var classes = '';
			var el = formOptions[i];

			// set classes to all classes in array
			for(var classI in el.classes) classes += el.classes + ' ';

			if(el.type === 'string') {
				// if this form option wants a string
				$('<input data-form-el-type="string" data-form-el="{formEl}" type="text" placeholder="{placeholder}" class="form-control {classes}" data-toggle="tooltip" data-placement="bottom" title="{tooltip}">'.format({
					formEl: i,
					placeholder: el.placeholder,
					classes: classes,
					tooltip: el.tooltip
				})).insertBefore('.btn-submit');
			} else if (el.type === 'select') {
				// if this form option wants a dropdown
				var optionsType = Object.prototype.toString.call(el.options); // is el.options an array or an object?

				// inserts the select at the end of the form
				$('<select data-form-el-type="string" data-form-el="{formEl}" name="{action}" id="job-{action}" class="form-control {classes}" data-toggle="tooltip" data-placement="bottom" title="{tooltip}"></select>'.format({
					formEl: i,
					action: i,
					classes: classes,
					tooltip: el.tooltip
				})).insertBefore('.btn-submit');

				// add a disabled header if one is set
				if(el.header) {
					$('.' + el.classes[0]).append('<option disabled>{text}</option>'.format({text: el.header}));
				}


				if(optionsType === '[object Array]') {
					// if the options supplied are an array
					for(var optionI = el.options.length-1; optionI > -1; optionI--) { // for each option, from last to first
						// put the <option> in the <select>
						$('.' + el.classes[0]).append('<option value="{index}">{text}</option>'.format({
							index: optionI,
							text: config.priorities[optionI]
						}));

					}
				} else if(optionsType === '[object Object]') {
					// if the options supplied are an object
					for(var optionJ in el.options) {
						// put the <option> in the <select>
						$('.' + el.classes[0]).append('<option value="{index}">{text}</option>'.format({
							index: optionJ,
							text: config.materials[optionJ]
						}));
					}
				}
			} else if (el.type === 'generic') {
				$(el.template).insertBefore('.btn-submit')
					.attr('data-form-el-type', 'generic')
					.attr('data-form-el', i);
				if(el.onRender) el.onRender();
			} else {
				// if this form option wants something we don't recognize (yet)
				logText('Unhandled input type: {type}.'.format({type: el.type}));
			}
		}

		// if there is a default material set
		if(config.defaultMaterial) {
			// select it
			$('.job-material').prop(
				'selectedIndex',
				$('.job-material').children('[value={material}]'.format({material: config.defaultMaterial})).index()
			);
		}

		// if there is a default priority set
		if(typeof config.defaultPriority === 'number') {
			// select it
			$('.job-priority').prop(
				'selectedIndex',
				$('.job-priority').children('[value={priority}]'.format({priority: config.defaultPriority})).index()
			);
		}

		// if not authed, disable privileged-only priorities
		if(!authed) {
			var priorityOptions = $('.job-priority').children(':not([disabled])');
			for(var p = 0; p < priorityOptions.length; p++) {
				if($(priorityOptions[p]).val() > config.highestPriorityAllowed && !config.priorityAllow) {
					$(priorityOptions[p]).prop('disabled', true);
				}
			}
		}

		// refill form based on cached values
		$('.form-group > *:not(.btn-submit)').each(function refillFormElements() {
			var formEl = formOptions[$(this).data('formEl')];
			try {
				if (formEl.cachedVal) $(this).val(formEl.cachedVal);
			} catch(e) {}
		});

		// focus the first form element on not-mobile
		if(!isTouchDevice()) $('.{formObject}:first'.format({formObject: formOptions.name.classes[0]})).focus();

		// reconfigure tooltips
		tooltips();

		// set up form submission
		$('.btn-submit').click(function submitForm(clickAction) {
			clickAction.preventDefault();
			logText("submit button clicked");
			NProgress.start(); // end when the sending callback is received
			var job = {
				"action": "add",
				"extras": {}
			};

			// for each direct child of '.form-group' that is not the submit button
			$('.form-group > *:not(.btn-submit)').each(function parseFormElements() {
				var formEl = $(this).data('formEl');

				if(!formOptions[formEl].noParse) {

					if (formEl === 'name' || formEl === 'material') {
						// if name or material, just send value
						job[formEl] = $(this).val();
					} else if (formEl === 'priority') {
						// if priority, send value as number
						job[formEl] = +$(this).val();
					} else  if (formEl === 'time'){
						// if time estimate, send value parsed as time and as number
						job[formEl] = +$('.job-time-estimate').val().match(/\d*(\.\d+)?/)[0];
					} else if (formEl) {
						// otherwise, toss into extras
						if($(this).data('formElType') === 'generic') {
							job.extras[formEl] = formOptions[formEl].getVal();
						} else {
							job.extras[formEl] = $(this).val();
						}
					}
				}
			});

			// send job to server and reset form
			socketSend(job);
			resetForm($('.new-job-form'));

			// focus name textbox
			$('.job-human-name').focus();
		});

		// configure <select>s in form to hide tooltip on click
		$('.job-form-group select').click(function hideTooltip() {
			$(this).tooltip('hide');
		});

		// cache current formOptions
		oldFormOptions = $.extend(true, formOptions);
	}
	$(queueEvents).trigger('form.rendered');
}

// wrapper for socketSend that changes an item's attribute
function changeAttr(taskid, attrKey, attrVal) {
	if(typeof taskid == 'string') {
		socketSend({
			'action': 'attr',
			'uuid': taskid,
			'key': attrKey,
			'new': attrVal
		});
	} else if(typeof taskid == 'number') {
		changeAttr(allCuts[taskid].uuid, attrKey, attrVal);
	} else if(typeof taskid == 'object') {
		changeAttr($(taskid).attr('data-uuid'), attrKey, attrVal);
	} else {
		logText('changeAttr() called with invalid taskid type');
	}
}

// read the function name, it says it all
function rickRoll() {
	if (config.easterEggs) {
		modalMessage('Never gonna give you up', '<iframe width="420" height="315" src="http://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&disablekb=1&controls=0&loop=1&showinfo=0&iv_load_policy=3" frameborder="0" allowfullscreen></iframe>');
		$('html').addClass('lol');
	}
	else {
		logText('This is a serious establishment, son. I\'m dissapointed in you.');
	}
}

// and his name is
function johnCena() {
	if (config.easterEggs) {
		modalMessage('And his name is', '<iframe width="420" height="315" src="https://www.youtube.com/embed/weBnn5fzcHg?autoplay=1&disablekb=1&controls=0&loop=1&showinfo=0&iv_load_policy=3" frameborder="0" allowfullscreen></iframe>');
	}
	else {
		logText('Too little cena, not enough easter egg.');
	}
}

// checks if the device is a touch device
function isTouchDevice(){
	return true === ('ontouchstart' in window || window.DocumentTouch && document instanceof DocumentTouch);
}

// ga() if Google Analytics is enabled
function googleAnalytics(i, s, o, g, r, a, m){
	if (typeof config.googleAnalyticsKey !== 'string' && config.googleAnalyticsKey !== '') {
		ga(i, s, o, g, r, a, m);
	}
}

// convert time in minutes to pretty time
function prettifyTime(mins) {
	var timetotal = mins;
	var hours = Math.floor(timetotal / 60);
	timetotal -= hours * 60;
	var minutes = Math.floor(timetotal);
	timetotal -= minutes;
	var seconds = +(timetotal * 60).toFixed(2);

	var prettyTime = String(hours ? hours + 'h' : '') + (minutes && hours ? ' ' : '');
	prettyTime += String(minutes ? minutes + 'm' : '') + (seconds && minutes ? ' ' : '');
	prettyTime += String(seconds ? seconds + 's' : '');

	return prettyTime;
}
