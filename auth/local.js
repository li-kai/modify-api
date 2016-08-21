const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const authenticationMiddleware = require('./middleware');

const init = require('./init');

passport.use(new LocalStrategy(
  function(username, password, done) {
    findUser(username, function (err, user) {
      if (err) {
        return done(err);
      }
      if (!user) {
        return done(null, false);
      }
      if (password !== user.password  ) {
        return done(null, false);
      }
      return done(null, user);
    });
  })
);

passport.authenticationMiddleware = authenticationMiddleware;

// serialize user into the session
init();

module.exports = passport;
