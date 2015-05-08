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
		rickRoll();
	};
	easterEgg.load();

	// or this:
	// easter_egg.load('https://www.youtube.com/watch?v=dQw4w9WgXcQ');

});