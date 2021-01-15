const Koa = require('koa');
const Router = require('koa-router');
const session = require('koa-generic-session');
const passport = require('koa-passport');
const views = require('koa-views');
const json = require('koa-json');
const onerror = require('koa-onerror');
const koaBody = require('koa-body');
const store = require('koa-sqlite3-session')

const app = new Koa();
const router = new Router();

// Utils
const fs = require('fs');
const glob = require('glob')
const path = require('path')

const config = require('./config');

// error handler
onerror(app)

// init uploads dir
if (!fs.existsSync(config.uploads)) {
  fs.mkdirSync(config.uploads);
}

// sessions
app.keys = ['i am a key you put me in lockxs']
app.use(session({
  store: new store(':memory:')
}, app));

// middlewares
app.use(koaBody({
  multipart: true,
  json: true,
  formLimit: config.max_upload_size,
  textLimit: config.max_upload_size,
  formidable: {
    maxFileSize: config.max_upload_size
  }
}))
  .use(json())
  .use(require('koa-static')(__dirname + '/public'))
  .use(views(path.join(__dirname, '/views'), {
    options: { settings: { views: path.join(__dirname, 'views') } },
    map: { 'pug': 'pug' },
    extension: 'pug'
  }));

// authentication
require('./auth')(passport);
app.use(passport.initialize());
app.use(passport.session());

// routes
glob.sync('./routes/*.js').forEach(function (file) {
  const route = require(path.resolve(file))
  route(router, passport)
});

app.use(router.routes())
  .use(router.allowedMethods())

module.exports = app.listen(config.port, config.host, () => {
  console.log(`Listening on http://${config.host}:${config.port}`);
})
