// put any utilities and functions here


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
		$(".log-pre").prepend("<span class='log-time'> [" + hoursZero + currentHours + ":" + minutesZero + currentMinutes + ":" + secondsZero + currentSeconds + "." + millisZero + currentMillis + "]:</span> " + text + "\n");
	}
}

// repopulate action button index
function populateActions() {
	$(".cutting-table-template tr td:nth-child(1)").each(function(index, el) {
		$(el).children('i').each(function(iIndex, iElement) {
			$(iElement).attr('data-uuid', allCuts[index].uuid);
			$(iElement).unbind('click');
		});
	});

	// reinitialize bootstrap tooltips
	$('[data-toggle="tooltip"]').tooltip();
	
	// handler to remove a job
	$(".remove-job").click(function() {
		logText("removing item " + $(this).attr("data-uuid"));
		socket.send(JSON.stringify({
			"action": "uremove",
			"args": [$(this).attr("data-uuid")],
			"sid": SID
		}));
	});

	// handler to lower a job
	$(".lower-priority").click(function() {
		logText("passing item " + $(this).attr("data-uuid"));
		socket.send(JSON.stringify({
			"action": "upass",
			"args": [$(this).attr("data-uuid")],
			"sid": SID
		}));
	});
}

// displays message in modal
function modalMessage(modalTitle, modalBody) {
	$('.notify-modal-title').html(modalTitle);
	$('.notify-modal-body').html(modalBody);
	$('#notify-modal').modal();
}

// reset a form
// with thanks to http://stackoverflow.com/questions/680241/resetting-a-multi-stage-form-with-jquery
function resetForm(form) {
	form.find('input:text, input:password, input:file, textarea').val(''); // removed 'select'
	form.find('input:radio, input:checkbox').removeAttr('checked').removeAttr('selected');
	if($(form).selector == ".new-cut-form") {
		// here is for resetting the form
		// later. maybe milestone 0.1.0
	}
}

function rickRoll() {
	if (easterEggs) {
		modalMessage('Never gonna give you up', '<iframe width="420" height="315" src="http://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&disablekb=1&controls=0&loop=1&showinfo=0&iv_load_policy=3" frameborder="0" allowfullscreen></iframe>');
		$('html').addClass('lol');
	}
	else {
		logText("This is a serious establishment, son. I'm dissapointed in you.");
	}
}