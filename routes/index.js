const express = require('express');
const router = express.Router();
const passport = require('passport');

const db = require('../queries');

router.get('/modules/:school/:year/:sem/:code', db.getSingleModule);
router.get('/modulesList/:school/:year/:sem', db.getModulesList);

router.get('/users', db.getUsersList);

router.post('/signup', passport.authenticate('local-signup'));

router.post('/authenticate', db.authenticateLocalUser);

module.exports = router;
