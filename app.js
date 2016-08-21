require('@risingstack/trace');
const express = require('express');
const path = require('path');
const logger = require('morgan');
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const expressValidator = require('express-validator');    // context validation
const passport = require('passport');   // passport for authentication
const session = require('express-session');   // session to save
const RedisStore = require('connect-redis')(session);
const config = require('./config');
const passportLocal = require('./auth/local');
// routes for api
const routes = require('./routes/index');

const app = express();

app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(expressValidator());
app.use(cookieParser());

app.use('/', routes);

app.use(session({  
  store: new RedisStore({
    url: config.redisStore.url
  }),
  secret: config.redisStore.secret,
  resave: false,
  saveUninitialized: false,
}));

app.use(passport.initialize());
app.use(passport.session());

app.get('/profile', passportLocal.authenticate('local'));
app.get('/profile/callback', passportLocal.authenticate('local'),
  function(req, res) {
    // Successful authentication
    res.json(req.user);
});

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  const err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handlers
/*
// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
  app.use(function(err, req, res, next) {
    res.status( err.code || 500 )
    .json({
      status: 'error',
      message: err
    });
  });
}
*/

// production error handler
// no stacktraces leaked to user
app.use(function(err, req, res, next) {
  res.status(err.status || 500)
  .json({
    status: 'error',
    message: err.message,
  });
});

module.exports = app;
