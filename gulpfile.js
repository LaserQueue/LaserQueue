var gulp         = require('gulp');
var sass         = require('gulp-sass');
var autoprefixer = require('gulp-autoprefixer');
var notify       = require('gulp-notify');
var jscs         = require('gulp-jscs');
var jscsStylish  = require('gulp-jscs-stylish');
var jshint       = require('gulp-jshint');
var noop         = function() {};
var uglify       = require('gulp-uglify');
var UglifyJS     = require('uglify-js');
var rename       = require('gulp-rename');
var concat       = require('gulp-concat');
var groupConcat  = require('gulp-group-concat');
var watch        = require('gulp-watch');
var sourcemaps   = require('gulp-sourcemaps');
var sizereport   = require('gulp-sizereport');

// compile sass
gulp.task('sass', function() {
	return gulp.src('./www/scss/styles.scss')
		.pipe(sourcemaps.init())
			.pipe(sass({outputStyle: 'compressed'}).on('error', sass.logError))
			.pipe(
				autoprefixer(
					'last 2 version',
					'safari 5',
					'ie 8',
					'ie 9',
					'opera 12.1',
					'ios 6',
					'android 4'
				)
			)
			.pipe(rename({suffix: '.min'}))
		.pipe(sourcemaps.write('.'))
	.pipe(gulp.dest('./www/css'))
	.pipe(notify({message: 'SCSS has been compiled'}))
});

// compile js
gulp.task('js', function() {
	return gulp.src(['./www/scripts/_functions.js', './www/scripts/_config.js', './www/scripts/_init.js', './www/scripts/_socketSetup.js', './www/scripts/_auth.js', './www/scripts/scripts.js'])
		.pipe(jshint())
		.pipe(sourcemaps.init())
			.pipe(jscs())
			.on('error', noop)
			.pipe(jscsStylish.combineWithHintResults())
			.pipe(concat('scripts.min.js'))
			.pipe(uglify())
		.pipe(sourcemaps.write('.'))
	.pipe(gulp.dest('./www/js/'))
	.pipe(notify({message: 'JS has been compiled'}))
	.pipe(jshint.reporter('jshint-stylish'));
});

// watch sass and compile
gulp.task('sass-watch', function() {
	gulp.start(['sass']);
	gulp.watch('./www/scss/*.scss', ['sass']);
});

// watch js and compile
gulp.task('js-watch', function() {
	gulp.start(['js']);
	gulp.watch('./www/scripts/*.js', ['js']);
});

// js size report
gulp.task('js-size-report', function() {
	gulp.src('./www/js/scripts.min.js').pipe(sizereport({gzip: true}));
});

// style size report
gulp.task('style-size-report', function() {
	gulp.src('./www/css/styles.min.css').pipe(sizereport({gzip: true}));
})

// overall size report
gulp.task('size', function() {
	gulp.start(['js-size-report', 'style-size-report']);
	gulp.src('./www/index.html').pipe(sizereport({gzip: true}));
})

// Default task, just runs dev
gulp.task('default', function() {
	gulp.start(['sass-watch', 'js-watch', 'size']).on('error', function() {});
});
