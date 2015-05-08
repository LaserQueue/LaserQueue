// main program with other stuff

// when jquery is here
$(document).ready(function() {

	// when submit button clicked
	$(".btn-submit").click(function(clickAction) {
		clickAction.preventDefault();
		logText("submit button clicked");
		socket.send('
			{
				"action": "add",
				"args": [
				"' + $(".cut-human-name").val() +'", ' + $(".priority-dropdown").val() + ', ' + $('.cut-time-estimate').val() + ', "' + $('.cut-material').val() + '"
				]
			}
		');
		resetForm($(".new-cut-form"));
		
	});

	var easterEgg = new Konami();
	easterEgg.code = function() {
		modalMessage('You goofed', '<iframe width="420" height="315" src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&disablekb=1&controls=0&loop=1&showinfo=0&iv_load_policy=3" frameborder="0" allowfullscreen></iframe>');
		$('html').addClass('lol');
	};
	easterEgg.load();

	// or this:
	// easter_egg.load('https://www.youtube.com/watch?v=dQw4w9WgXcQ');

});