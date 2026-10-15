import assert from "node:assert/strict";
import { beforeEach, test } from "node:test";
import { defaults } from "../src/config.js";
import { deepCopy } from "../src/utils.js";
import { state, setState } from "../src/state.js";
import { el, normalizeState, setSelection, selectedItems, overlaps, findChannelGaps, inferGapDelays, validateState } from "../src/model.js";
import { magneticStart, magneticDuration } from "../src/snapping.js";

beforeEach(() => setState(deepCopy(defaults)));

test("imports preserve legacy colors and correlated selection while removing orphan elements", () => {
  const project = normalizeState({
    channels: [{ id: "a", name: "1H" }, { id: "b", name: "13C" }, { id: "c", name: "15N" }],
    elements: [{ id: "pulse", channel: "a", color: "red", alpha: 2 }, { id: "orphan", channel: "missing" }],
    selectedId: "pulse", selectedIds: ["pulse", "orphan", "pulse"], activeChannelId: "missing"
  });
  assert.deepEqual(project.channels.map(channel => channel.value), [3, 1.5, 0]);
  assert.equal(project.elements.length, 1);
  assert.equal(project.elements[0].facecolor, "red");
  assert.equal(project.elements[0].alpha, 1);
  assert.equal("color" in project.elements[0], false);
  assert.deepEqual(project.selectedIds, ["pulse"]);
  assert.equal(project.selectedId, "pulse");
  assert.equal(project.activeChannelId, "a");
});

test("multi-selection filters invalid IDs and tracks the primary element", () => {
  state.elements = [el("pulse", "ch-f1", 0, 1), el("pulse", "ch-f2", 0, 1)];
  const [a, b] = state.elements;
  setSelection([a.id, b.id, a.id, "missing"], a.id);
  assert.deepEqual(selectedItems(), [a, b]);
  assert.equal(state.selectedId, a.id);
  setSelection([]);
  assert.equal(state.selectedId, null);
});

test("gap detection merges occupied intervals and ignores marker and rotor overlays", () => {
  state.elements = [el("pulse", "ch-f1", 2, 2), el("pulse", "ch-f1", 3, 2), el("pulse", "ch-f1", 7, 1), el("marker", "ch-f1", 1, 0), el("rotor", "ch-f1", 0, 8)];
  assert.deepEqual(findChannelGaps("ch-f1"), [{ start: 0, duration: 2 }, { start: 5, duration: 2 }]);
  assert.deepEqual(findChannelGaps("ch-f2"), []);
  const inferred = inferGapDelays([state.elements[0], state.elements[2]], "ch-f1");
  assert.equal(inferred[1].type, "delay");
  assert.equal(inferred[1].start, 4);
  assert.equal(inferred[1].duration, 3);
});

test("overlap validation allows touching edges, separate channels, and overlays", () => {
  const pulse = el("pulse", "ch-f1", 0, 2, { allowOverlap: false });
  const other = el("pulse", "ch-f1", 2, 2, { allowOverlap: false });
  state.elements = [pulse, other, el("rotor", "ch-f1", 0, 10)];
  assert.equal(overlaps(pulse), null);
  other.start = 1;
  assert.equal(overlaps(pulse), other);
  assert.equal(validateState().length, 1);
  other.channel = "ch-f2";
  assert.equal(overlaps(pulse), null);
  pulse.duration = 0;
  assert.match(validateState()[0], /non-positive duration/);
});

test("magnetic snapping aligns pulse boundaries and Shift falls back to the grid", () => {
  const moving = el("pulse", "ch-f1", 0, 1);
  state.elements = [moving, el("pulse", "ch-f2", 4, 2)];
  const metrics = { xScale: 100 };
  const snapped = magneticStart(moving, 3.05, metrics);
  assert.equal(snapped.value, 3);
  assert.equal(snapped.guide.time, 4);
  assert.equal(magneticDuration(moving, 3.95, metrics).value, 4);
  assert.deepEqual(magneticStart(moving, 3.12, metrics, true), { value: 3, guide: null });
});
