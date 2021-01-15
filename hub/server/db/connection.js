const config = require('../config/knex.js')['dev'];

module.exports = require('knex')(config);