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
	$('.cut-human-name').focus();
}

// when submit button clicked
$('.btn-submit').click(function submitForm(clickAction) {
	clickAction.preventDefault();
	logText("submit button clicked");
	var estimate = $('.cut-time-estimate').val().match(/\d*(\.\d+)?/);
	socketSend({
			'action': 'add',
			'args': [
				$('.cut-human-name').val(),
				+$('.priority-dropdown').val(),
				+estimate[0],
				$('.cut-material').val()
			]
		});
	resetForm($('.new-cut-form'));
	$('.cut-human-name').focus();

});

// bind ESC key to hide all dialogs
$(document).keyup(function hideAllDialogs(e) {
	if (e.keyCode == 27) {
		bootbox.hideAll();
	}
});

// ready the konami
$(document).ready(function loadKonami() {
	var easterEgg = new Konami();
	easterEgg.code = function rickRollUser() {
		rickRoll();
	};
	easterEgg.load();
});
