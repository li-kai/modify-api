const express = require('express');
const router = express.Router();

const db = require('../queries');

router.get('/api/modules/:school/:year/:sem/:code', db.getSingleModule);
router.get('/api/modulesList/:school/:year/:sem', db.getModulesList);

module.exports = router;