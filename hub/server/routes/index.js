const repoQueries = require('../db/queries/repo');
const { checkAuthenticated } = require('./utils/auth');

module.exports = (router) => {
  router.get('/', async (ctx, next) => {
    ctx.state = {
      title: 'Hub',
      authenticated: checkAuthenticated(ctx)
    };
    await ctx.render('index', ctx.state);
  });

  router.get('/upload', async (ctx, next) => {
    await repoQueries.getModelTypes()
      .then(async types => {
        await repoQueries.getDatasetSlugs()
          .then(datasets => {
            ctx.state = {
              title: 'Hub - Upload',
              types: types,
              datasets: datasets,
              authenticated: checkAuthenticated(ctx)
            };
          })
      });
    await ctx.render('upload', ctx.state);
  });

  router.get('/search', async (ctx, next) => {
    const query = ctx.query.q;
    if (query == undefined) {
      ctx.state = {
        title: 'Hub - Search',
        query: '',
        results: [],
        authenticated: checkAuthenticated(ctx)
      };
    } else {
      ctx.params.query = query;
      await repoQueries.searchDataset(ctx)
        .then(results => {
          results.forEach(x => x['resultType'] = 'dataset');
          return results;
        })
        .then(async datasetResults => {
          await repoQueries.searchModel(ctx)
            .then(results => {
              results.forEach(x => x['resultType'] = 'model');
              return results;
            })
            .then(modelResults => {
              ctx.state = {
                title: 'Hub - Search',
                query: query,
                results: modelResults.concat(datasetResults),
                authenticated: checkAuthenticated(ctx)
              };
            });
        })
    }
    await ctx.render('search', ctx.state);
  });

}
