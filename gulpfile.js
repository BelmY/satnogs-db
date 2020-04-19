/* global require */

const gulp = require('gulp');

const lintPathsJS = [
    'db/static/js/*.js',
    'gulpfile.js'
];

const lintPathsCSS = [
    'db/static/css/*.css'
];

gulp.task('js:lint', function() {
    const eslint = require('gulp-eslint');

    return gulp.src(lintPathsJS)
        .pipe(eslint())
        .pipe(eslint.format());
});

gulp.task('css:lint', function() {
    const stylelint = require('gulp-stylelint');

    return gulp.src(lintPathsCSS)
        .pipe(stylelint({
            reporters: [{ formatter: 'string', console: true}]
        }));
});

gulp.task('assets', function() {
    const p = require('./package.json');
    const assets = p.assets;

    return gulp.src(assets, {cwd : 'node_modules/**'})
        .pipe(gulp.dest('db/static/lib'));
});

gulp.task('test', gulp.parallel('js:lint', 'css:lint'));

gulp.task('default', gulp.series('assets', 'test'));
