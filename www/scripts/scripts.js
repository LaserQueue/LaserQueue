// main program

// when jquery is here
$(document).ready(function documentIsReady() {

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

	var easterEgg = new Konami();
	easterEgg.code = function rickRollUser() {
		rickRoll();
	};
	easterEgg.load();

	// or this:
	// easter_egg.load('https://www.youtube.com/watch?v=dQw4w9WgXcQ');

});