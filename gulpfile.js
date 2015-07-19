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
var fileinclude  = require('gulp-file-include');
var watch        = require('gulp-watch');
var sourcemaps   = require('gulp-sourcemaps');
var manifest     = require('gulp-manifest');
var sizereport   = require('gulp-sizereport');

// compile sass
gulp.task('sass', function() {
	return gulp.src('./www/lib/scss/styles.scss')
		.pipe(sourcemaps.init())
			.pipe(sass({outputStyle: 'compressed'}).on('error', sass.logError))
			.pipe(autoprefixer('last 2 version', 'safari 5', 'ie 8', 'ie 9', 'opera 12.1', 'ios 6', 'android 4'))
			.pipe(rename({suffix: '.min'}))
		.pipe(sourcemaps.write('.'))
	.pipe(gulp.dest('./www/dist/css'))
	.pipe(notify({message: 'SCSS has been compiled'}))
});

// compile js for development
gulp.task('js-dev', function() {
	gulp.src('./www/lib/scripts/_*.js')
		.pipe(jshint())
		.pipe(jscs())
		.pipe(jscsStylish.combineWithHintResults())
		.pipe(jshint.reporter('jshint-stylish'));
	gulp.src(['./www/lib/scripts/libraries.js', './www/lib/scripts/_*.js'])
		.pipe(sourcemaps.init())
		.pipe(fileinclude())
			.on('error', noop)
			.pipe(concat('scripts.min.js'))
		.pipe(sourcemaps.write('.'))
	.pipe(gulp.dest('./www/dist/js/'))
	.pipe(notify({message: 'JS has been compiled for development'}))
});

// compile js for production
gulp.task('js-prod', function() {
	gulp.src(['./www/lib/scripts/libraries.js', './www/lib/scripts/_*.js'])
		.pipe(sourcemaps.init())
		.pipe(fileinclude())
			.on('error', noop)
			.pipe(concat('scripts.min.js'))
			.pipe(uglify())
		.pipe(sourcemaps.write('.'))
	.pipe(gulp.dest('./www/dist/js/'))
	.pipe(notify({message: 'JS has been compiled for production'}))
});

// watch sass and compile
gulp.task('sass-watch', function() {
	gulp.start(['sass']);
	gulp.watch('./www/lib/scss/*.scss', ['sass']);
});

// watch js and compile
gulp.task('js-watch', function() {
	gulp.start(['js-dev']);
	gulp.watch('./www/lib/scripts/*.js', ['js-dev']);
	gulp.watch('./.jscsrc', ['js-dev']);
});

// make cache manifest
gulp.task('manifest', function() {
	return gulp.src(['./www/'])
		.pipe(manifest({
			hash: true,
			timestamp: true,
			preferOnline: true,
			network: ['*', 'app.manifest', 'index.html'],
			filename: 'app.manifest',
			exclude: ['app.manifest', 'index.html'],
			cache: [
				'dist/img/logo.svg',
				'dist/img/laserQueue.png',
				'bower_components/js-sha1/build/sha1.min.js',
				'bower_components/bootstrap/dist/fonts/glyphicons-halflings-regular.woff2',
				'bower_components/bootstrap/dist/css/bootstrap.min.css',
				'bower_components/bootstrap/dist/js/bootstrap.min.js',
				'bower_components/jquery/dist/jquery.min.js'
			]
		}))
		.pipe(gulp.dest('./www'));
})

// watch and make cache manifest
gulp.task('manifest-watch', function() {
	gulp.watch('./www/**/*', ['manifest']);
});

// js size report
gulp.task('js-size-report', function() {
	gulp.src('./www/dist/js/scripts.min.js').pipe(sizereport({gzip: true}));
});

// style size report
gulp.task('style-size-report', function() {
	gulp.src('./www/dist/css/styles.min.css').pipe(sizereport({gzip: true}));
})

// overall size report
gulp.task('size', function() {
	gulp.start(['js-size-report', 'style-size-report']);
	gulp.src('./www/index.html').pipe(sizereport({gzip: true}));
})

// Default task, just runs dev
gulp.task('default', function() {
	gulp.start(['sass-watch', 'js-watch']).on('error', function() {});
});
