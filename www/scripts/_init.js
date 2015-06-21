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
.done(function(request) {
	$('.credits-footer').before(
		marked(request)
	);
})
.fail(function() {
	console.log('Failed to get infotext.md');
});

// focus the first form element on not-mobile
if(!isTouchDevice()) {
	$('.cut-human-name').focus();
}