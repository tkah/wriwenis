
/* File: gulpfile.js */

// grab our gulp packages
var gulp  = require('gulp'),
    gutil = require('gulp-util'),
    sourcemaps = require('gulp-sourcemaps'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    cleanCSS = require('gulp-clean-css');
    jade = require('jade');
    gulpJade = require('gulp-jade');

gulp.task('build-css', function() {
    return gulp.src([
      'src/reset.css',
      'node_modules/angular-material/angular-material.min.css',
      'static/styles.css'
    ])
    .pipe(gutil.env.type === 'dev' ? sourcemaps.init() : gutil.noop())
    .pipe(cleanCSS())
    .pipe(concat('styles.min.css'))
    .pipe(gutil.env.type === 'dev' ? sourcemaps.write() : gutil.noop())
    .pipe(gulp.dest('static'))
});

gulp.task('build-sitejs', function() {
    return gulp.src('src/js/*.js')
        .pipe(gutil.env.type === 'dev' ? sourcemaps.init() : gutil.noop())
        .pipe(concat('site-bundle.min.js'))
        .pipe(uglify())
        .pipe(gutil.env.type === 'dev' ? sourcemaps.write() : gutil.noop())
        .pipe(gulp.dest('static'));
});

gulp.task('build-jsimports', function() {
    return gulp.src([
      'node_modules/angular-animate/angular-animate.min.js',
      'node_modules/angular-aria/angular-aria.min.js',
      'node_modules/angular-fontawesome/dist/angular-fontawesome.min.js',
      'node_modules/angular-animate/angular-animate.min.js',
      'node_modules/angular-material/angular-material.min.js',
      'node_modules/angular-messages/angular-messages.min.js',
      'node_modules/angular-ui-router/release/angular-ui-router.min.js',
      'node_modules/angularjs-scroll-glue/src/scrollglue.js'
    ])
    .pipe(concat('imports-bundle.min.js'))
    .pipe(gulp.dest('static'));
});

gulp.task('build-html', function() {
  var LOCALS = {};

  return gulp.src('src/jade/*.jade')
    .pipe(gulpJade({
        locals: LOCALS
    }))
    .pipe(gulp.dest('templates'));
})
