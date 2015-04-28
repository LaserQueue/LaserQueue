// put any utilities and functions here

// logs text to devlog on page
function logText(text) {

	$(function() {
		var currentTime = new Date();
		$(".log").append("<span class='log-time'>" + currentTime.getHours() + ":" + currentTime.getMinutes() + " " + currentTime.getSeconds() + "s " + currentTime.getMilliseconds() + "ms </span> " + text + "\n");
	});
}

// populates actions with buttons
function populateActions() {
	$(".cutting-table tr:not(.table-first-row) td:nth-child(1)").each(function(index, el) {
		$(el).html('
			<i data-index="' + index + '" class="glyphicon glyphicon-remove remove-job" data-toggle="tooltip" data-placement="right" title="Cancel this job"></i>
			<i data-index="' + index + '" class="glyphicon glyphicon-triangle-bottom lower-priority" data-toggle="tooltip" data-placement="right" title="Move job down"></i>
		');
	});
	$('[data-toggle="tooltip"]').tooltip();
	
	// handler to remove a job
	$(".remove-job").mouseup(function() {
		console.log("removing attribute " + $(this).attr("data-index"));
		socket.send(JSON.stringify({
			"action": "sremove",
			"args": [+$(this).attr("data-index")]
		}));
	});

	// handler to lower a job
	$(".lower-priority").mouseup(function() {
		console.log("removing attribute " + $(this).attr("data-index"));
		socket.send(JSON.stringify({
			"action": "spass",
			"args": [+$(this).attr("data-index")]
		}));
	});
}

// displays message in modal
function modalMessage(modalTitle, modalBody) {
	$('.notify-modal-title').html(modalTitle);
	$('.notify-modal-body').html(modalBody);
	$('#notify-modal').modal();
}