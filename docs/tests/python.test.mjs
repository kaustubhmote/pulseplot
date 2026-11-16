import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { beforeEach, test } from "node:test";
import { state, setState } from "../src/state.js";
import { el, normalizeState } from "../src/model.js";
import { templates } from "../src/templates.js";
import { generatePython } from "../src/python.js";

const baseline = JSON.parse(await readFile(new URL("./fixtures/python.json", import.meta.url), "utf8"));
beforeEach(() => setState(normalizeState(null)));

for (const [name, project] of Object.entries(templates)) {
  test(`${name} produces the same Python as the original standalone page`, () => {
    setState(normalizeState(project));
    assert.equal(generatePython(), baseline[name]);
  });
}

test("custom envelopes and rotors produce executable API calls with styles", () => {
  state.elements = [
    el("shaped", "ch-f1", 0, 2, { shape: "custom", facecolor: "red", hatch: "///", alpha: .5 }),
    el("rotor", "ch-f2", 3, 2)
  ];
  const code = generatePython();
  assert.match(code, /import numpy as np/);
  assert.match(code, /shape=lambda x: np.interp/);
  assert.match(code, /facecolor="red"/);
  assert.match(code, /al=0.5 h=\/\/\//);
  assert.match(code, /ax.rotor\(axdims=\[4, 0.5, 1.5\], length=2\)/);
});

test("Python strings escape user-entered titles and preserve math annotations", () => {
  state.settings.title = 'An "echo"\nsecond line';
  state.elements = [el("pulse", "ch-f1", 0, 1, { text: String.raw`$\tau$ # label` })];
  const code = generatePython();
  assert.ok(code.includes('fig.suptitle("An \\"echo\\"\\nsecond line"'));
  assert.ok(code.includes(String.raw`tx=\`$\tau$ ＃ label\``.replaceAll("\\`", "`")));
});
