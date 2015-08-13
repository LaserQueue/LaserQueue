// initialize the things

// holds old and new JSON
// for comparison to minimize layout thrashing n stuff
var oldJsonData = 'uninitialized';
var jsonData;

// initialize the modal by changing the title
$('.notify-modal-title').html('Notification');

// footer
$.ajax({
	url: '/infotext.md',
	type: 'GET'
})
.done(function writeInfoText(request) {
	$('.credits-footer').before(
		marked(request)
	);
})
.fail(function handleInfoTextFail() {
	console.log('Failed to get infotext.md');
});

// focus the first form element on not-mobile
if(!isTouchDevice()) {
	$('.job-human-name').focus();
}

// bind ESC key to hide all dialogs
$(document).keyup(function hideAllDialogs(e) {
	if (e.keyCode == 27) {
		bootbox.hideAll();
		$('.remove-job').popover('hide');
	}
});

// allow click-hold on log button to download logs so far
var logClickTimeout = 0;

$('.log-toggler').mousedown(function maybeDownloadLog(evt) {
	if(evt.altKey) {
		logClickTimeout = setTimeout(function downloadLog() {
			window.open('data:application/octet-stream;,' + encodeURI($('.log-pre').text()));
		}, 1000);
	}
}).bind('mouseup mouseleave', function doNotDownloadLog() {
	clearTimeout(logClickTimeout);
});

// ready the konami
$(document).ready(function loadKonami() {
	var easterEgg = new Konami();
	easterEgg.code = function rickRollUser() {
		rickRoll();
	};
	easterEgg.load();
});
