const { HTTP_HOST, HTTP_PORT } = process.env;

module.exports = {
  host: HTTP_HOST || '127.0.0.1',
  port: HTTP_PORT || 3000,
  uploads: './upload',
  max_upload_size: 10 * 1024 * 1024 * 1024 // 10GB
}
