/* global require */

var gulp = require('gulp');
var eslint = require('gulp-eslint');
var stylelint = require('gulp-stylelint');

var lintPathsJS = [
    'db/static/js/*.js',
    'gulpfile.js'
];

var lintPathsCSS = [
    'db/static/css/*.css'
];

gulp.task('js:lint', () => {
    return gulp.src(lintPathsJS)
        .pipe(eslint())
        .pipe(eslint.format())
        .pipe(eslint.failAfterError());
});

gulp.task('css:lint', () => {
    return gulp.src(lintPathsCSS)
        .pipe(stylelint({
            reporters: [{ formatter: 'string', console: true}]
        }));
});

gulp.task('assets', function(){
    var p = require('./package.json');
    var assets = p.assets;
    return gulp.src(assets, {cwd : 'node_modules/**'})
        .pipe(gulp.dest('db/static/lib'));
});

gulp.task('test', function(){
    gulp.start('js:lint');
    gulp.start('css:lint');
});

gulp.task('default', function() {
    gulp.start('assets');
    gulp.start('test');
});
