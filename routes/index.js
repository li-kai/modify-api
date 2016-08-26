const express = require('express');
const router = express.Router();
const passport = require('passport');

const db = require('../queries');

router.get('/modules/:school/:year/:sem/:code', db.getSingleModule);
router.get('/modulesList/:school/:year/:sem', db.getModulesList);

router.get('/users', db.getUsersList);

router.post('/signup', passport.authenticate('local-signup', {
        successRedirect : '/profile', // redirect to the secure profile section
        failureRedirect : '/signup', // redirect back to the signup page if there is an error
        failureFlash : true // allow flash messages
    }));


module.exports = router;
