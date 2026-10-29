const http = require("http");
const fs = require("fs");
const path = require("path");

const root = __dirname;
const port = 4175;
const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".webm": "video/webm",
  ".mp4": "video/mp4"
};

http.createServer((request, response) => {
  const requestedPath = decodeURIComponent((request.url || "/").split("?")[0]);
  const relativePath = requestedPath === "/" ? "/index.html" : requestedPath;
  const filePath = path.resolve(root, `.${relativePath}`);

  if (filePath !== root && !filePath.startsWith(`${root}${path.sep}`)) {
    response.writeHead(403);
    response.end("Forbidden");
    return;
  }

  fs.readFile(filePath, (error, file) => {
    if (error) {
      response.writeHead(error.code === "ENOENT" ? 404 : 500);
      response.end(error.code === "ENOENT" ? "Not found" : "Server error");
      return;
    }

    response.writeHead(200, {
      "Content-Type": contentTypes[path.extname(filePath).toLowerCase()] || "application/octet-stream"
    });
    response.end(file);
  });
}).listen(port, "127.0.0.1", () => {
  console.log(`Agentic AI For Work is available at http://127.0.0.1:${port}/index.html`);
});
