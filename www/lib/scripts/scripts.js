// main program

// libraries first
@@include('../../bower_components/jquery/dist/jquery.min.js')
@@include('../../bower_components/bootstrap/dist/js/bootstrap.min.js')
@@include('../../bower_components/transparency/dist/transparency.min.js')
@@include('../../bower_components/node-uuid/uuid.js')
@@include('../../bower_components/js-sha1/build/sha1.min.js')
@@include('../../bower_components/marked/marked.min.js')
@@include('../../bower_components/draggabilly/dist/draggabilly.pkgd.min.js')

// general functions and utilities
@@include('_functions.js')

// config loading and parsing
@@include('_config.js')

// initialization
@@include('_init.js')

// socket communication setup
@@include('_socketSetup.js')

// authentication and coachmode
@@include('_auth.js')

// syntax highlighting
@@include('prism.js')

// konami code handling
@@include('konami.js')


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