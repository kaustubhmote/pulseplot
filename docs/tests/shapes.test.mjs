import assert from "node:assert/strict";
import { test } from "node:test";
import { SHAPE_SPECS } from "../src/config.js";
import { parseShape, composeShape, shapeValues, interpolate } from "../src/shapes.js";
import { displayMath } from "../src/math.js";

test("shape parameters retain defaults and round-trip through the editor", () => {
  assert.deepEqual(parseShape("unknown").params, [.5, .1667]);
  assert.equal(composeShape("tan", [50, .1]), "tan_50_0.1");
  assert.deepEqual(parseShape(composeShape("ramp", [-40])).params, [-40]);
});

test("every supported envelope produces finite, ordered samples over the full duration", () => {
  for (const shape of Object.keys(SHAPE_SPECS)) {
    const points = shapeValues({ shape, customPoints: [[0, 0], [.5, 1], [1, 0]] });
    assert.equal(points[0][0], 0, shape);
    assert.equal(points.at(-1)[0], 1, shape);
    assert.ok(points.every(([x, y], index) => Number.isFinite(y) && Math.abs(y) <= 1.35 && (!index || x >= points[index - 1][0])), shape);
  }
});

test("ramp direction, custom interpolation, and FID sample density are preserved", () => {
  const ramp = shapeValues({ shape: "ramp_-40" });
  assert.equal(ramp[0][1], 1);
  assert.equal(ramp.at(-1)[1], .6);
  assert.equal(interpolate([[1, 0], [0, 0], [.5, 1]], .25), .5);
  assert.equal(shapeValues({ shape: "fid_100_5" }).length, 2401);
  assert.equal(shapeValues({ shape: "fid_1000_5" }).length, 4097);
});

test("math annotations display Greek letters and scripts", () => {
  assert.equal(displayMath(String.raw`$\phi_{1} + \tau^2$`), "φ₁ + τ²");
  assert.equal(displayMath(String.raw`$90^{\circ}$`), "90°");
});
