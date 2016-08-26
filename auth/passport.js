// auth/passport.js
        
// load all the things we need
const db = require('../queries');
const bcrypt = require('bcrypt');
const LocalStrategy = require('passport-local').Strategy;

// expose this function to our app using module.exports
module.exports = function(passport) {

  // =========================================================================
  // passport session setup ==================================================
  // =========================================================================
  // required for persistent login sessions
  // passport needs ability to serialize and unserialize users out of session

  // used to serialize the user for the session
  passport.serializeUser((user, done) => {
    done(null, user.id);
  });

  // used to deserialize the user
  passport.deserializeUser((id, done) => {
    db.getSingleUserById(id).then((user) => {
      done(null, user);
    }).catch((error) => {
      console.log(error);
      done(error, null);
    });
  });

  // =========================================================================
  // LOCAL SIGNUP ============================================================
  // =========================================================================
  // we are using named strategies since we have one for login and one for signup
  // by default, if there was no name, it would just be called 'local'

  passport.use('local-signup', new LocalStrategy({
    // by default, local strategy uses username and password, we will override with email
    usernameField : 'email',
    passwordField : 'password',
    passReqToCallback : true // allows us to pass back the entire request to the callback
  }, registerUser));
  
  function registerUser(req, email, password, done) {
    // asynchronous
    // User.findOne wont fire unless data is sent back
    process.nextTick(() => {
      
    // find a user whose email is the same as the forms email
    // we are checking to see if the user trying to login already exists
    db.getSingleUserByEmail(email).then((user) => {
      // user exists // TODO: reroute them to log in if password is correct
      if (user) {
        console.log('User already in db');
        return done(null, false, req.flash('signupMessage', 'That email is already taken.'));
      }
      // if there is no user with that email
      // create the user
      bcrypt.hash(password, 10, (err, hash) => {
        // Store hash in your password DB.
        const newUser = {
          email,
          password: hash,
        };
        
        console.log('Made new user');
        if (err) {
          console.log(err);
          return done(err, null);
        }
        
        db.setSingleUser(email, hash).then((id) => {
          newUser.id = id;
          return done(null, newUser);
        }).catch((error) => {
          console.log(error);
          return done(error, null);
        });
      });
    }).catch((error) => {
      if (error) {
        return done(error);
      }
    });
    });
  }

  // =========================================================================
  // LOCAL LOGIN =============================================================
  // =========================================================================
  // we are using named strategies since we have one for login and one for signup
  // by default, if there was no name, it would just be called 'local'
  /*
  passport.use('local-login', new LocalStrategy({
    // by default, local strategy uses username and password, we will override with email
    usernameField : 'email',
    passwordField : 'password',
    passReqToCallback : true // allows us to pass back the entire request to the callback
  },
  function(req, email, password, done) { // callback with email and password from our form

     connection.query("SELECT * FROM `users` WHERE `email` = '" + email + "'",function(err,rows){
      if (err)
        return done(err);
       if (!rows.length) {
        return done(null, false, req.flash('loginMessage', 'No user found.')); // req.flash is the way to set flashdata using connect-flash
      } 
      
      // if the user is found but the password is wrong
      if (!( rows[0].password == password))
        return done(null, false, req.flash('loginMessage', 'Oops! Wrong password.')); // create the loginMessage and save it to session as flashdata
      
      // all is well, return successful user
      return done(null, rows[0]);			
    
    });
    
  }));
  */
};