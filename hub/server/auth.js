const LocalStrategy = require('passport-local').Strategy;
const bcrypt = require('bcryptjs');

const knex = require('./db/connection');

const options = {};

function comparePass(userPassword, databasePassword) {
    return bcrypt.compareSync(userPassword, databasePassword);
}

module.exports = (passport) => {

    passport.serializeUser((user, done) => { done(null, user.username); });

    passport.deserializeUser((username, done) => {
        return knex('user_basic').where('username', username).first()
            .then((user) => { done(null, user); })
            .catch((err) => { done(err, null); });
    });

    passport.use(new LocalStrategy(options, (username, password, done) => {
        knex('user_basic').where('username', username).first()
            .then((user) => {
                if (!user) return done(null, false);
                if (!comparePass(password, user.password)) {
                    return done(null, false);
                } else {
                    return done(null, user);
                }
            })
            .catch((err) => { return done(err); });
    }));

}