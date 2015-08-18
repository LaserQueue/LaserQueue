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


function ensureNumberStringLength(number, len) {
	return '0'.repeat(len - String(number).length) + String(number);
}

// logs text to devlog on page
function logText(text) {
	if(config.dev_log) {
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
		$('[data-toggle="tooltip"]').tooltip();
	}

	// handler to remove a job
	$('.remove-job').click(function handleRemove(event) {
		// remove job based on action button
		var removeJob = function removeJob(actionButton) {
			googleAnalytics('send', 'event', 'action', 'click', 'remove job');
			logText('removing item {uuid}'.format({uuid: $($(this).parents()[1]).attr('data-uuid')}));
			socketSend({
				'action': 'remove',
				'uuid': $(actionButton).parents('tr').attr('data-uuid')
			});
		};
		if(event.altKey) {
			removeJob(this);
		} else {
			$(event.toElement).tooltip('hide');
			$('.remove-job').popover('hide');
			$(event.toElement).popover({
				placement: 'bottom',
				html: true,
				content: function confirmModalContents() {
					return '<button class="btn btn-default btn-lg btn-block cancel-remove">No</button>' +
						'<button class="btn btn-danger btn-lg btn-block confirm-remove">Yes</button>';
				}
			});
			$(event.toElement).popover('show');
			$('.confirm-remove').focus();
			$('.cancel-remove').click(function cancelRemove(event) {
				$('.remove-job').popover('hide');
			});
			$('.confirm-remove').click(function confirmRemove(event) {
				removeJob(this);
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
				$('[data-toggle="tooltip"]').tooltip('destroy');
				$('.jobs-table-template tr:not(.is-dragging) td:nth-child(1) a.glyphicon').addClass('animate-hide');
			});
			$(this).on('dragEnd', function handleDragEnd(event, pointer) {
				$('.jobs-table-template tr:not(.is-dragging) td:nth-child(1) a.glyphicon').removeClass('animate-hide');
				$('[data-toggle="tooltip"]').tooltip();
				socketSend({
					'action': 'relmove',
					'uuid': $(this).attr('data-uuid'),
					'target_index': parseInt($(this).attr('data-pos')) + parseInt(Math.round($(this).data('draggabilly').position.y / 37))

				});
			});
		});
	}
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
		if (event.toElement.id === 'notify-modal') {
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
	logText('rendering form');
	$('.job-form-group').html('<button type="submit" class="btn btn-default btn-pink btn-submit">Submit</button>');
	for(var i in formOptions) {
		var classes = '';
		var el = formOptions[i];
		for(var classI in el.classes) classes += el.classes + ' ';
		if(el.type === 'string') {
			$('<input type="text" placeholder="{placeholder}" class="form-control {classes}" data-toggle="tooltip" data-placement="bottom" title="{tooltip}">'.format({
				placeholder: el.placeholder,
				classes: classes,
				tooltip: el.tooltip
			})).insertBefore('.btn-submit');
		} else if (el.type === 'select') {
			$('<select name="{action}" id="job-{action}" class="form-control {classes}" data-toggle="tooltip" data-placement="bottom" title="{tooltip}"></select>'.format({
				action: i,
				classes: classes,
				tooltip: el.tooltip
			})).insertBefore('.btn-submit');
		} else {
			logText('Unhandled input type: {type}.'.format({type: el.type}));
		}
	}

	// render materials dropdown
	if (!config.default_material) {
		$('#job-material').append('<option disabled selected value="N/A" class="selected">{text}</option>'.format({text: config.material_input}));
	}
	
	for(var m in config.materials) {
		var mat_selected = (m === config.default_material ? 'selected' : '');
		$('#job-material').append('<option {selected} value="{index}" class="{selected}">{text}</option>'.format({
			selected: mat_selected,
			index: m,
			text: config.materials[m]}));
	}

	// render the priorities dropdown
	if (config.priority_choose) {
		$('#job-priority').append('<option disabled selected value="-1" class="selected">{text}</option>'.format({text: config.priority_input}));
	}
	for(var p = config.priorities.length-1; p > -1; p--) {
		var disabled = (p > config.default_priority && !config.priority_selection ? 'disabled' : '');
		var pri_selected = (p == config.default_priority && !config.priority_choose ? 'selected' : '');
		$('#job-priority').append('<option {selected} value="{index}" class="{disabled} {selected}">{text}</option>'.format({
			selected: pri_selected,
			index: p,
			disabled: disabled,
			text: config.priorities[p]}));
	}
	if (!config.priority_selection) {
		$('.disabled').prop('disabled', true);
	}

	// focus the first form element on not-mobile
	if(!isTouchDevice()) $('.' + formOptions.name.classes[0] + ':first').focus();

	// reconfigure tooltips
	$('.form-group').children('[data-toggle="tooltip"]').tooltip();

	// set up form submission
	$('.btn-submit').click(function submitForm(clickAction) {
		clickAction.preventDefault();
		logText("submit button clicked");
		var estimate = $('.job-time-estimate').val().match(/\d*(\.\d+)?/);
		socketSend({
			'action': 'add',
			'name': $('.job-human-name').val(),
			'priority': +$('.job-priority').val(),
			'time': +estimate[0],
			'material': $('.job-material').val()
		});
		resetForm($('.new-job-form'));
		$('.job-human-name').focus();
	});

	// configure <select>s in form to hide tooltip on click
	$('.job-form-group select').click(function hideTooltip() {
		$(this).tooltip('hide');
	});
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
	if (config.easter_eggs) {
		modalMessage('Never gonna give you up', '<iframe width="420" height="315" src="http://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&disablekb=1&controls=0&loop=1&showinfo=0&iv_load_policy=3" frameborder="0" allowfullscreen></iframe>');
		$('html').addClass('lol');
	}
	else {
		logText('This is a serious establishment, son. I\'m dissapointed in you.');
	}
}

// checks if the device is a touch device
function isTouchDevice(){
	return true === ('ontouchstart' in window || window.DocumentTouch && document instanceof DocumentTouch);
}

// ga() if Google Analytics is enabled
function googleAnalytics(i, s, o, g, r, a, m){
	if (typeof config.google_analytics_key !== 'string' && config.google_analytics_key !== '') {
		ga(i, s, o, g, r, a, m);
	}
}
