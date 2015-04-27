// main program

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
	});

});