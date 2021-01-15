const { DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME } = process.env;

module.exports = {
  dev: {
    client: 'pg',
    connection: {
      host: DB_HOST || '127.0.0.1',
      user: DB_USER || 'postgres',
      password: DB_PASSWORD || 'password',
      database: DB_NAME || 'postgres',
      port: DB_PORT || 6543
    }
  }
};
