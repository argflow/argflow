const bcrypt = require('bcryptjs');
const knex = require('../connection');

function getSingleUser(id) {
  return knex('user_basic')
    .select('*')
    .where({ id: parseInt(id) });
}

function addUser(user) {
  const salt = bcrypt.genSaltSync();
  const hash = bcrypt.hashSync(user.password, salt);
  return knex('user_basic')
    .insert({
      username: user.username,
      password: hash,
    })
    .returning('id');
}

module.exports = {
  getSingleUser,
  addUser,
};