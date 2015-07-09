// put any utilities and functions etc in here

if (!String.prototype.format) {
	String.prototype.format = function stringPrototypeFormat() {
		var args = arguments;
		return this.replace(/{(\d+)}/g, function matchWithNumber(match, number) {
			return typeof args[number] != 'undefined' ? args[number] : match;
		});
	};
}
if (!String.prototype.repeat) {
	String.prototype.repeat = function countThrough(count) {
		'use strict';
		if (this === null) {
			throw new TypeError('can\'t convert ' + this + ' to object');
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
	var currentTime = new Date();
	var currentDay = ensureNumberStringLength(currentTime.getDate(), 2);
	var currentMonth = months[currentTime.getMonth()];
	var currentYear = currentTime.getFullYear();
	var currentHours = ensureNumberStringLength(currentTime.getHours(), 2);
	var currentMinutes = ensureNumberStringLength(currentTime.getMinutes(), 2);
	var currentSeconds = ensureNumberStringLength(currentTime.getSeconds(), 2);

	var timestamp = '[{0}/{1}/{2} {3}:{4}:{5}] '.format(currentDay, currentMonth, currentYear,
		currentHours, currentMinutes, currentSeconds);
	if(devLog) {

		var textArray = text.split('\n');

		for (var i = textArray.length - 1; i > 0; i--) {
			$('.log-pre').prepend('<span class="log-time">' + ' '.repeat(23) + '</span> ' + textArray[i] + '\n');
		}
		$('.log-pre').prepend('<span class="log-time"> ' + timestamp + '</span>' + textArray[0] + '\n');
	} else {
		window.console.log(timestamp+text);
	}
}

// repopulate action button UUIDs
function populateActions() {
	logText('Populating actions');

	$('.cutting-table-template tr').each(function dataToTable(index, el) {
		$(el).attr('data-uuid', allCuts[index].uuid);
		$(el).attr('data-pos', index);
		$(el).unbind('click');
	});

	// reinitialize bootstrap tooltips
	if(isTouchDevice() === false) {
		$('[data-toggle="tooltip"]').tooltip();
	}

	// handler to remove a job
	$('.remove-job').click(function removeJob() {
		googleAnalytics('send', 'event', 'action', 'click', 'remove job');
		logText('removing item ' + $($(this).parents()[1]).attr('data-uuid'));
		socketSend({
			'action': 'remove',
			'args': [$($(this).parents()[1]).attr('data-uuid')]
		});
	});

	// asks before it removes a job
	$('.remove-job').popConfirm({
		content: "Remove this job?",
		placement: "bottom"
	});

	// handler to lower a job
	$('.lower-priority').click(function lowerPriority() {
		googleAnalytics('send', 'event', 'action', 'click', 'pass job');
		logText('passing item ' + $($(this).parents()[1]).attr('data-uuid'));
		socketSend({
			'action': 'pass',
			'args': [$($(this).parents()[1]).attr('data-uuid')]
		});
	});

	// handler to decrement a job
	$('.decrement-job').click(function decrementJob() {
		googleAnalytics('send', 'event', 'action', 'click', 'decrement job');
		logText('removing item ' + $($(this).parents()[1]).attr('data-uuid'));
		socketSend({
			'action': 'decrement',
			'args': [$($(this).parents()[1]).attr('data-uuid')]
		});
	});

	// handler to increment a job
	$('.increment-job').click(function incrementJob() {
		googleAnalytics('send', 'event', 'action', 'click', 'increment job');
		logText('passing item ' + $($(this).parents()[1]).attr('data-uuid'));
		socketSend({
			'action': 'increment',
			'args': [$($(this).parents()[1]).attr('data-uuid')]
		});
	});

	if (authed || config.authactions.indexOf('relmove') == -1) {
		$('.cutting-table-template tr').each(function makeRowsDraggable(index, el) {
			draggable[index] = this;
			$(this).draggabilly({
				axis: 'y',
				container: $('.cutting-table-template')//,
				// grid: [ 37, 37 ]
			});
			$(this).on('dragStart', function handleDragStart() {
				$('[data-toggle="tooltip"]').tooltip('destroy');
				$('.cutting-table-template tr:not(.is-dragging) td:nth-child(1) a.glyphicon').addClass('animate-hide');
			});
			$(this).on('dragEnd', function handleDragEnd(event, pointer) {
				$('.cutting-table-template tr:not(.is-dragging) td:nth-child(1) a.glyphicon').removeClass('animate-hide');
				$('[data-toggle="tooltip"]').tooltip();
				socketSend({
					'action': 'relmove',
					'args': [
						$(this).attr('data-uuid'),
						parseInt($(this).attr('data-pos')) + parseInt(Math.round($(this).data('draggabilly').position.y / 37))
					]
				});
			});
		});
	}
}

// displays message in a bootstrap modal
function modalMessage(modalTitle, modalBody) {
	// hide all dialogs up
	bootbox.hideAll();

	// show the dialog with message and title
	bootbox.dialog({
		title: modalTitle,
		message: modalBody
	});

	// spoof our homebaked old modalMessage()
	$('.bootbox').attr('id', 'notify-modal');
	$('.modal-title').addClass('notify-modal-title');
	$('.modal-title').attr('id', 'notify-modal-label');
	$('.modal-body').addClass('notify-modal-body');

	// bind clicking background to hide modal
	$('.bootbox').click(function bgClickHideModals() {
		bootbox.hideAll();
	});
}

// reset a form with thanks to http://stackoverflow.com/questions/680241/resetting-a-multi-stage-form-with-jquery
function resetForm(form) {
	form.find('input:text, input:password, input[type=number], input:file, textarea').val(''); // removed 'select'
	form.find('input:radio, input:checkbox').removeAttr('checked').removeAttr('selected');
	if($(form).selector == '.new-cut-form') {
		form.find('.selected').prop('selected', true);
	}
}

// adds SID to JSON and sends over websockets if the connection is stable
function socketSend(jdata) {
	// if a session ID has been set and the socket is ready
	if(typeof SID != "undefined" && socket.readyState == 1) {
		jdata.sid = SID;
		socket.send(JSON.stringify(jdata));
	} else {
		// if not sending, log why
		if(typeof SID != "undefined") {
			logText("socketSend() has been called, but SID is undefined.");
		}
		if(socket.readyState != 1) {
			logText("socketSend() has been called, but socket.readyState is not 1. The socket is probably not connected yet.");
		}
	}
}

// wrapper for socketSend that changes an item's attribute
function changeAttr(taskid, attrKey, attrVal) {
	if(typeof taskid == 'string') {
		socketSend({
			'action': 'attr',
			'args': [taskid, attrKey, attrVal]
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
	if (easterEggs) {
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
