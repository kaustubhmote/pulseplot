import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
const docsDir = fileURLToPath(new URL("../", import.meta.url));

const contentTypes = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".json": "application/json" };

export function createDevServer() {
  return createServer(async (request, response) => {
    try {
      const url = new URL(request.url, "http://localhost");
      if (url.pathname === "/") {
        response.writeHead(302, { Location: "/src/index.html" }).end();
        return;
      }
      const pathname = decodeURIComponent(url.pathname);
      const filename = path.resolve(docsDir, "." + pathname);
      if (!filename.startsWith(docsDir) || pathname.includes("\\")) {
        response.writeHead(403).end("Forbidden");
        return;
      }
      const content = await readFile(filename);
      response.writeHead(200, { "Content-Type": contentTypes[path.extname(filename)] || "application/octet-stream", "Cache-Control": "no-store" });
      response.end(content);
    } catch (error) {
      response.writeHead(error.code === "ENOENT" || error.code === "EISDIR" ? 404 : 400).end("File unavailable");
    }
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT || 4173);
  const server = createDevServer();
  server.on("error", error => { console.error(error.message); process.exitCode = 1; });
  server.listen(port, "127.0.0.1", () => {
    console.log(`Source preview: http://127.0.0.1:${server.address().port}/`);
    console.log(`Built page:     http://127.0.0.1:${server.address().port}/index.html`);
  });
}
