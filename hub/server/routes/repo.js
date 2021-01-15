const fs = require('fs');
const path = require('path');
const send = require('koa-send');

const authUtils = require('./utils/auth');
const repoQueries = require('../db/queries/repo');

const config = require('../config');

const uploadFile = ctx => {
    const file = ctx.request.files.file;
    const uploadPath = path.join(config.uploads, Math.random().toString());
    const reader = fs.createReadStream(file.path);
    const stream = fs.createWriteStream(uploadPath);
    reader.pipe(stream);
    return uploadPath;
}

module.exports = (router, passport) => {

    router.get('/api/model/search/:query', async (ctx) => {
        const res = await repoQueries.searchModel(ctx);
        ctx.body = res;
    });

    router.post('/api/model', async (ctx) => {
        if (authUtils.checkAuthenticated(ctx)) {
            ctx.request.body.author = ctx.state.user.id;
            ctx.request.body.location = uploadFile(ctx);
            await repoQueries.addModel(ctx);
            ctx.body = 'uploaded model!';
        } else {
            ctx.body = 'please log in';
        }
    });

    router.get('/api/model/:query', async (ctx) => {
        const res = await repoQueries.getModel(ctx);
        ctx.body = res;
    });

    router.get('/api/model/:query/download', async (ctx) => {
        const res = await repoQueries.downloadModel(ctx);
        await send(ctx, res);
    });

    router.get('/api/dataset/search/:query', async (ctx) => {
        const res = await repoQueries.searchDataset(ctx);
        ctx.body = res;
    });

    router.post('/api/dataset', async (ctx) => {
        if (authUtils.checkAuthenticated(ctx)) {
            ctx.request.body.author = ctx.state.user.id;
            ctx.request.body.location = uploadFile(ctx);
            await repoQueries.addDataset(ctx);
            ctx.body = 'uploaded dataset!';
        } else {
            ctx.body = 'please log in';
        }
    });

    router.get('/api/dataset/:query', async (ctx) => {
        const res = await repoQueries.getDataset(ctx);
        ctx.body = res;
    });

    router.get('/api/dataset/:query/download', async (ctx) => {
        const res = await repoQueries.downloadDataset(ctx);
        await send(ctx, res);
    });

}