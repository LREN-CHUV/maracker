'use strict';

var gulp = require('gulp');
var webpackStream = require('webpack-stream');
var webpack2 = require('webpack');
var sass = require('gulp-sass');
var cleanCSS = require('gulp-clean-css');
var browserSync = require('browser-sync').create();
var util = require('gulp-util');

var config = {
  production: !!util.env.production
}

const path = require('path');

const BabiliPlugin = require("babili-webpack-plugin");

const HtmlWebpackPlugin = require('html-webpack-plugin');
const HtmlWebpackPluginConfig = new HtmlWebpackPlugin({
  template: './templates/index.html',
  filename: 'index.html',
  inject: 'body'
})

var webpackConfig = {
  entry: './js/index.js',
  output: {
    path: path.resolve('dist'),
    filename: 'js/index_bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        use: [
          {
            loader: 'babel-loader',
          }
        ],
        exclude: [
          path.resolve(__dirname, 'node_modules/')
        ]
      },
      {
        test: /\.jsx$/,
        use: [
          {
            loader: 'babel-loader',
          }
        ],
        exclude: [
          path.resolve(__dirname, 'node_modules/')
        ]
      }
    ]
  },
  plugins: [HtmlWebpackPluginConfig]
}

if (config.production == true) {
  webpackConfig.plugins.push(new BabiliPlugin())
}

console.log(webpackConfig.plugins)

// Static Server + watching scss/html files
gulp.task('serve', ['sass'], function() {
    browserSync.init({
        server: "./dist"
    });

    gulp.watch("scss/*.scss", ['sass']);
    gulp.watch("js/*.js", ['webpack']);
    gulp.watch("js/components/*.jsx", ['webpack']);
    gulp.watch("templates/*.html").on('change', browserSync.reload);
});


gulp.task('webpack', function() {
  return gulp.src('js/index.js')
    .pipe(webpackStream(webpackConfig, webpack2))
    .pipe(gulp.dest('dist'))
    .pipe(browserSync.stream());
});

gulp.task('sass', function () {
  return gulp.src('./sass/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(config.production ? cleanCSS() : util.noop())
    .pipe(gulp.dest('./dist/css'))
    .pipe(browserSync.stream());
});

gulp.task('default', ['serve']);
