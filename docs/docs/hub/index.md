# ArgHub

## Install and Run Locally
Simply run:

```bash
docker-compose up -d
```

!!! warning
    If you are the developer and deploying ArgHub in production, be sure to update
    the hub endpoint in the library (found under `argflow/hub/_api.py`).


## Configuration
There are two configuration files: `server/config/index.js` and `server/config/knex.js`. The former allows you to configure the server parameters including host, port, upload location and maximum upload size (for models and datasets). The latter allows you to specify database connection settings.