const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = (app) => {
  // Proxy websocket connections under /ws
  app.use(createProxyMiddleware("ws://localhost:8000/ws"));

  // Proxy HTTP requests under /api and /modules
  ["/api", "/modules"].map((path) =>
    app.use(
      path,
      createProxyMiddleware({
        target: "http://localhost:8000",
      })
    )
  );
};
