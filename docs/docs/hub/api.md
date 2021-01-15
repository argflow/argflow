# Arghub API Reference

## Authentication

!!! warning
    In production, this must be done over HTTPS.

### Registration
You can create a new account.

```haskell
POST /auth/register
```
The registration endpoint expects a form-data body with the following fields:

- `username` - a username
- `password` - a password


### Logging In
You can authenticate a session.

```haskell
POST /auth/login
```

The login endpoint expects a form-data body with the following fields:

- `username` - a username
- `password` - a password

### Logging Out
You can deauthenticate a session.

```haskell
GET /auth/logout
```


## Repository

### Searching

You can search for models and datasets. Results are returned in JSON format. 
For models, this includes the model name, author, type, slug, description and also, if applicable, the slug of the dataset
the model was trained on. For datasets, this includes the dataset name, author, slug and description.

```haskell
GET /api/model/search/:query
GET /api/dataset/search/:query
```

### Downloading

You can download models and datasets.
```haskell
GET /api/model/search/:query/download
GET /api/dataset/search/:query/download
```

### Uploading

!!! warning
    Requires authentication.

You can upload models and datasets.
```haskell
POST /api/model
POST /api/dataset
```

The model endpoint expects a `multipart/form-data` body with the following fields:

- `name` - the model name
- `slug` - a model slug
- `type` - a model type id (corresponding to the id stored in the database)
- `dataset` - the dataset id (corresponding to the id stored in the database)
- `description` - the model description
- `file` - a .zip archive containing the packaged model (see [Model Packaging](../../argflow/portal))


The dataset endpoint expects a `multipart/form-data` body with the following fields:

- `name` - the model name
- `slug` - a dataset slug
- `description` - the model description
- `file` - a .zip archive containing the dataset in an HDF5 file.