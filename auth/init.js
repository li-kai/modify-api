const passport = require('passport');

const user = {
  username: 'test-user',
  password: 'test-password',
  id: 1,
};

module.exports = function() {
  passport.serializeUser(function (user, done) {
    done(null, user.username);
  });

  passport.deserializeUser(function (username, done) {
    if (username === user.username) {
      return done(null, user);
    }
    return done(null);
  });
};
