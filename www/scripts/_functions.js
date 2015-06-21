// put any utilities and functions etc in here


// logs text to devlog on page
function logText(text) {
	if(devLog) {
		var currentTime = new Date();
		var currentHours = currentTime.getHours();
		var currentMinutes = currentTime.getMinutes();
		var currentSeconds = currentTime.getSeconds();
		var currentMillis = currentTime.getMilliseconds();

		var hoursZero = (currentHours < 10 ? '0' : '');
		var minutesZero = (currentMinutes < 10 ? '0' : '');
		var secondsZero = (currentSeconds < 10 ? '0' : '');
		var millisZero = (currentMillis < 10 ? '00' : currentMillis < 100 ? '0' : '');
		var timestamp = '[' + hoursZero + currentHours + ':' + minutesZero + currentMinutes + ':' + secondsZero + currentSeconds + '.' + millisZero + currentMillis + ']';

		var textArray = text.split('\n');

		for (var i = textArray.length - 1; i >= 0; i--) {
			$('.log-pre').prepend('<span class="log-time"> ' + timestamp + ':</span> ' + textArray[i] + '\n');
		}
	} else {
		window.console.log('DevLog Redirect: [' + text + ']');
	}
}

// repopulate action button UUIDs
function populateActions() {
	logText('Populating actions');

	$('.cutting-table-template tr').each(function(index, el) {
		$(el).attr('data-uuid', allCuts[index].uuid);
		$(el).attr('data-pos', index);
		$(el).unbind('click');
	});

	// reinitialize bootstrap tooltips
	if(isTouchDevice() === false) {
		$('[data-toggle="tooltip"]').tooltip();
	}

	// handler to remove a job
	$('.remove-job').click(function() {
		googleAnalytics('send', 'event', 'action', 'click', 'remove job');
		logText('removing item ' + $($(this).parents()[1]).attr('data-uuid'));
		socketSend({
			'action': 'remove',
			'args': [$($(this).parents()[1]).attr('data-uuid')]
		});
	});

	// handler to lower a job
	$('.lower-priority').click(function() {
		googleAnalytics('send', 'event', 'action', 'click', 'pass job');
		logText('passing item ' + $($(this).parents()[1]).attr('data-uuid'));
		socketSend({
			'action': 'pass',
			'args': [$($(this).parents()[1]).attr('data-uuid')]
		});
	});

	// handler to decrement a job
	$('.decrement-job').click(function() {
		googleAnalytics('send', 'event', 'action', 'click', 'decrement job');
		logText('removing item ' + $($(this).parents()[1]).attr('data-uuid'));
		socketSend({
			'action': 'decrement',
			'args': [$($(this).parents()[1]).attr('data-uuid')]
		});
	});

	// handler to increment a job
	$('.increment-job').click(function() {
		googleAnalytics('send', 'event', 'action', 'click', 'increment job');
		logText('passing item ' + $($(this).parents()[1]).attr('data-uuid'));
		socketSend({
			'action': 'increment',
			'args': [$($(this).parents()[1]).attr('data-uuid')]
		});
	});

	if (authed || config.authactions.indexOf('relmove') == -1) {
		$('.cutting-table-template tr').each(function(index, el) {
			draggable[index] = this;
			$(this).draggabilly({
				axis: 'y',
				container: $('.cutting-table-template')//,
				// grid: [ 37, 37 ]
			});
			$(this).on('dragStart', function() {
				$('[data-toggle="tooltip"]').tooltip('destroy');
				$('.cutting-table-template tr:not(.is-dragging) td:nth-child(1) a.glyphicon').addClass('animate-hide');
			});
			$(this).on('dragEnd', function(event, pointer) {
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
	$('.notify-modal-title').html(modalTitle);
	$('.notify-modal-body').html(modalBody);
	$('#notify-modal').modal();
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
