import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "node:test";
import { Script } from "node:vm";
import { synthesize } from "../scripts/build.mjs";

test("the committed document matches a deterministic, self-contained build", async () => {
  const html = await synthesize();
  assert.equal(html, await synthesize());
  assert.equal(html, await readFile(new URL("../index.html", import.meta.url), "utf8"));
  assert.doesNotMatch(html, /<script[^>]+src=|<link[^>]+rel="stylesheet"/);
  assert.match(html, /script-src 'unsafe-inline'/);
  const javascript = html.match(/<script>\n([\s\S]*?)\n  <\/script>/)[1];
  assert.doesNotThrow(() => new Script(javascript));
});

test("all source modules link without browser globals at import time", async () => {
  for (const name of ["events", "exports", "commands", "canvas", "inspector", "interactions"]) {
    await import(`../src/${name}.js`);
  }
});
