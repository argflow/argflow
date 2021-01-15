const queries = require('../db/queries/user');
const authUtils = require('./utils/auth');

module.exports = (router, passport) => {

    router.post('/auth/register', async (ctx) => {
        const user = await queries.addUser(ctx.request.body);
        return passport.authenticate('local', (err, user, info, status) => {
            if (user) {
                ctx.login(user);
                ctx.redirect('/');
            } else {
                ctx.status = 400;
                ctx.body = { status: 'error' };
            }
        })(ctx);
    });

    router.post('/auth/login', async (ctx) => {
        return passport.authenticate('local', (err, user, info, status) => {
            if (user) {
                ctx.login(user);
                ctx.redirect('/');
            } else {
                ctx.status = 400;
                ctx.body = { status: 'error' };
            }
        })(ctx);
    });

    router.get('/login', async (ctx, next) => {
        if (authUtils.checkAuthenticated(ctx)) {
            ctx.redirect('/');
        } else {
            const register = ctx.request.query.register;
            ctx.state = {
                title: 'Hub - Login',
                register: register != undefined,
                authenticated: false
            };
        }
        await ctx.render('login', ctx.state);
    });


    router.get('/auth/logout', async (ctx) => {
        if (authUtils.checkAuthenticated(ctx)) {
            ctx.logout();
            ctx.redirect('/');
        } else {
            ctx.body = { success: false };
            ctx.throw(401);
        }
    });
}
