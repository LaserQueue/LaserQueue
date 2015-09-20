var tour = new Shepherd.Tour({
	defaults: {
		classes: 'shepherd-theme-arrows',
		showCancelLink: true
	}
});

tour.addStep('LaserQueue', {
	title: 'Welcome to LaserQueue',
	text: 'This site keeps track of everything that needs to be lasercut.',
	attachTo: 'body center'
});

tour.addStep('name', {
	title: 'Adding a new cut',
	text: 'First, enter your name',
	attachTo: '.job-human-name bottom',
	when: {
		show: function focusEl() {
			$('.job-human-name').focus().tooltip('hide');
		}
	}
});

tour.addStep('time', {
	title: 'Adding a new cut',
	text: 'Next, estimate the length of the cut in minutes',
	attachTo: '.job-time-estimate bottom',
	when: {
		show: function focusEl() {
			$('.job-time-estimate').focus().tooltip('hide');
		}
	}
});

tour.addStep('material', {
	title: 'Adding a new cut',
	text: 'What material are you cutting?',
	attachTo: '.job-material bottom',
	when: {
		show: function focusEl() {
			$('.job-material').focus().tooltip('hide');
		}
	},
	advanceOn: '.job-material change'
});

tour.addStep('priority', {
	title: 'Adding a new cut',
	text: 'You can lower your cut\'s priority. Coaches can also raise it.',
	attachTo: '.job-priority bottom',
	when: {
		show: function focusEl() {
			$('.job-priority').focus().tooltip('hide');
		}
	},
	advanceOn: '.job-material change'
});

tour.addStep('submit', {
	title: 'Submitting your cut',
	text: 'To add your cut to the queue, just hit submit!',
	attachTo: '.btn-submit bottom',
	when: {
		show: function focusEl() {
			$('.btn-submit').focus().tooltip('hide');
		}
	},
	advanceOn: '.btn-submit click',
	buttons: []
});

tour.addStep('removal', {
	title: 'Removing a job',
	text: 'You can click <i class="fa fa-remove remove-job"></i> to remove a job. Don\'t  try that right now!',
	attachTo: '.remove-job right'
});

tour.addStep('lowering', {
	title: 'Lowering a job',
	text: 'You can lower your job with <i class="fa fa-chevron-down"></i>',
	attachTo: '.lower-priority right'
});

tour.addStep('conclusion', {
	title: 'Good luck',
	text: 'If you have any questions, be sure to ask a coach!',
	attachTo: 'body center'
});

tour.on('complete', function bringBackTooltips() {
	$('body').removeClass('hide-tooltips');
});

tour.on('cancel', function bringBackTooltips() {
	$('body').removeClass('hide-tooltips');
});

function queueTour() {
	if (config.allow_tour) {
		$('body').addClass('hide-tooltips');
		tour.start();
	} else {
		logText("The tour isn't enabled.");
	}
}
