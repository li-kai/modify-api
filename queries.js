const promise = require('bluebird');
const path = require('path');
const user = require('./user');
const expressValidator = require('express-validator');

// Initialization Options for pg-promise
const options = {
  promiseLib: promise
};

// Connection Params for pg-promise
const connectionParams = {
    host: 'localhost',
    port: 5432,
    database: 'modify',
    user: user.username,
    password: user.password
};

const pgp = require('pg-promise')(options);
const db = pgp(connectionParams);

// Helper for linking to external query files:  
function sql(file) {
    const fullPath = path.join(__dirname, file) 
    return new pgp.QueryFile(fullPath, {debug: true});
}

// Create QueryFile globally, once per file: 
const sqlFindModule = sql('./sql/module.sql');
const sqlModuleList = sql('./sql/module_list.sql');

// Schema for common fields
const checkSchema = {
 'school': {
    notEmpty: true,
    matches: {
      // case insensitve
      options: ['NTU|NUS', 'i']
    },
    errorMessage: 'Invalid school, must be NTU or NUS',
  },
  'year': {
    notEmpty: true,
    isInt: {
      options: [{ min: 2010, max: 2050 }],
    },
    errorMessage: 'Invalid year, must be between 2010 and 2050',
  },
  'sem': {
    notEmpty: true,
    isInt: {
      options: [{ min: 1, max: 4 }],
    },
    errorMessage: 'Invalid sem, must be 1 - 4',
  },
};

function respondWithErrors(errors, res) {
  const response = { errors: [] };
  errors.forEach(err => {
    response.errors.push(err.msg);
  });
  res.statusCode = 400;
  return res.json(response);
}

function getSingleModule(req, res, next) {
  req.checkParams(checkSchema);
  req.checkParams('code', 'Must be between 2 and 10 chars long')
    .notEmpty().isLength({ min: 2, max: 10 })
    .isAlphanumeric();
  
  const errors = req.validationErrors();
  if (errors) {
    return respondWithErrors(errors, res);
  }

  const school = req.params.school.toUpperCase();
  const year = parseInt(req.params.year, 10);
  const sem = parseInt(req.params.sem, 10);
  const code = req.params.code.toUpperCase();

  db.one(sqlFindModule, {school, year, sem, code})
    .then(function (data) {
      res.status(200).json(data);
    })
    .catch(function (error) {
      // output no data as 404 instead of 500
      if (error.result &&
        'rowCount' in error.result &&
        error.result.rowCount === 0) {
        error.status = 404;
      }
      return next(error);
    });
}

function getModulesList(req, res, next) {
  req.checkParams(checkSchema);
  
  const errors = req.validationErrors();
  if (errors) {
    return respondWithErrors(errors, res);
  }

  const school = req.params.school.toUpperCase();
  const year = parseInt(req.params.year, 10);
  const sem = parseInt(req.params.sem, 10);

  db.any(sqlModuleList, {school, year, sem})
    .then(function (data) {
      res.status(200).json(data);
    })
    .catch(function (error) {
      return next(error);
    });
}


module.exports = {
  getSingleModule,
  getModulesList
};
