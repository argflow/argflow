const knex = require('../connection');

function getModelTypes() {
  return knex('model_type')
    .select('id', 'name');
}

function getDatasetSlugs() {
  return knex('dataset')
    .select('id', 'slug');
}

function searchModel(ctx) {
  const query = ctx.params.query;
  return knex('model')
    .leftJoin('user_basic', 'author', 'user_basic.id')
    .leftJoin('model_type', 'model_type.id', 'model.type')
    .leftJoin('dataset', 'dataset.id', 'model.dataset')
    .select('model.name as name', 'user_basic.username as author', 'model_type.name as type', 'dataset.slug as dataset', 'model.description as description', 'model.slug as slug')
    .where('model.name', 'like', `%${query}%`)
    .orWhere('model.slug', 'like', `%${query}%`)
}

function getModel(ctx) {
  const query = ctx.params.query;
  const query_int = parseInt(query);
  return knex
    .select('model.name as name', 'model.slug as slug', 'model_type.name as type', 'username as author', 'model.description as description')
    .from('model')
    .where(isNaN(query_int) ? { 'model.slug': query } : { 'model.id': query_int })
    .leftJoin('user_basic', 'author', 'user_basic.id')
    .leftJoin('dataset', 'dataset', 'dataset.id')
    .leftJoin('model_type', 'type', 'model_type.id');
}

function downloadModel(ctx) {
  const query = ctx.params.query;
  const query_int = parseInt(query);
  return knex('model_version')
    .leftJoin('model', 'model.id', 'model_version.model')
    .select('location')
    .where(isNaN(query_int) ? { 'model.slug': query } : { 'model.id': query_int })
    .orderBy('uploaded_at', 'desc')
    .first()
    .then(res => {
      return res.location;
    });
}

function addModel(ctx) {
  const body = ctx.request.body;
  knex('model')
    .insert({
      name: body.name,
      slug: body.slug,
      type: body.type,
      author: body.author,
      dataset: body.dataset,
      description: body.description
    })
    .returning('id')
    .then((id) => {
      return knex('model_version')
        .insert({
          model: parseInt(id),
          uploaded_at: 'now()',
          location: body.location
        })
    });
  return true;
}

function searchDataset(ctx) {
  const query = ctx.params.query;
  return knex('dataset')
    .leftJoin('user_basic', 'user_basic.id', 'dataset.author')
    .select('dataset.name as name', 'dataset.slug as slug', 'user_basic.username as author', 'dataset.description as description')
    .where('dataset.name', 'like', `%${query}%`)
    .orWhere('dataset.slug', 'like', `%${query}%`)
}

function getDataset(ctx) {
  const query = ctx.params.query;
  const query_int = parseInt(query);
  return knex
    .select('name', 'slug', 'username as author', 'description')
    .from('dataset')
    .where(isNaN(query_int) ? { 'dataset.slug': query } : { 'dataset.id': query_int })
    .leftJoin('user_basic', 'author', 'user_basic.id');
}

function downloadDataset(ctx) {
  const query = ctx.params.query;
  const query_int = parseInt(query);
  return knex('dataset_version')
    .leftJoin('dataset', 'dataset.id', 'dataset_version.dataset')
    .select('location')
    .where(isNaN(query_int) ? { 'dataset.slug': query } :  { 'dataset_version.dataset': query_int })
    .orderBy('uploaded_at', 'desc')
    .first()
    .then(res => {
      return res.location;
    });
}

function addDataset(ctx) {
  const body = ctx.request.body;
  return knex('dataset')
    .insert({
      name: body.name,
      slug: body.slug,
      author: body.author,
      description: body.description
    })
    .returning('id')
    .then((id) => {
      return knex('dataset_version')
        .insert({
          dataset: parseInt(id),
          uploaded_at: 'now()',
          location: body.location
        })
    });
}

module.exports = {
  getModelTypes,
  getDatasetSlugs,
  searchModel,
  getModel,
  downloadModel,
  addModel,
  searchDataset,
  getDataset,
  downloadDataset,
  addDataset
};