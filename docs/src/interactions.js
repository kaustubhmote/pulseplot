import { $, deepCopy, uid, round, clamp } from "./utils.js";
import { state, runtime } from "./state.js";
import { el, snapshot, selected, setSelection, isElementSelected, overlaps } from "./model.js";
import { checkpoint } from "./history.js";
import { changed, renderAll, renderCode } from "./render.js";
import { canvasMetrics, channelAtY } from "./svg.js";
import { magneticStart, magneticDuration } from "./snapping.js";
import { renderCanvas } from "./canvas.js";
import { renderInspector, renderShapeEditor } from "./inspector.js";
import { addElement } from "./commands.js";
import { toast } from "./notifications.js";

export function pointerToSvg(event, svg = $("#sequenceCanvas")) {
  const point = svg.createSVGPoint();
  point.x = event.clientX; point.y = event.clientY;
  return point.matrixTransform(svg.getScreenCTM().inverse());
}

export function beginCanvasInteraction(event) {
  const group = event.target.closest("[data-element-id]");
  if (!group || event.button > 0) return;
  event.preventDefault();
  const checkpointState = snapshot();
  let item = state.elements.find(candidate => candidate.id === group.dataset.elementId);
  if (!item) return;
  if ((event.ctrlKey || event.metaKey) && !event.altKey) return;
  if (event.altKey) {
    item = { ...deepCopy(item), id: uid("el") };
    state.elements.push(item);
    setSelection([item.id], item.id);
  } else if (isElementSelected(item.id)) {
    setSelection(state.selectedIds, item.id);
  } else {
    setSelection([item.id], item.id);
  }
  state.activeChannelId = item.channel;
  const handle = event.target.dataset.handle;
  const point = pointerToSvg(event);
  runtime.interaction = { id: item.id, mode: handle || "move", origin: point, initial: deepCopy(item), checkpoint: checkpointState, invalid: false, snapGuide: null };
  $("#sequenceCanvas").setPointerCapture(event.pointerId);
  renderAll();
}

export function moveCanvasInteraction(event) {
  if (!runtime.interaction) return;
  const item = state.elements.find(candidate => candidate.id === runtime.interaction.id);
  if (!item) return;
  const point = pointerToSvg(event), m = canvasMetrics();
  const dx = (point.x - runtime.interaction.origin.x) / m.xScale;
  if (runtime.interaction.mode === "duration") {
    const result = magneticDuration(item, runtime.interaction.initial.duration + dx, m, event.shiftKey);
    item.duration = result.value;
    runtime.interaction.snapGuide = result.guide;
  }
  else if (runtime.interaction.mode === "amplitude") {
    const dy = runtime.interaction.origin.y - point.y;
    item.amplitude = round(clamp(runtime.interaction.initial.amplitude + dy / 58, -1.5, 1.5), 2);
    runtime.interaction.snapGuide = null;
  } else {
    const result = magneticStart(item, runtime.interaction.initial.start + dx, m, event.shiftKey);
    item.start = result.value;
    runtime.interaction.snapGuide = result.guide;
    const channel = channelAtY(point.y, m);
    item.channel = channel.id;
    state.activeChannelId = channel.id;
  }
  runtime.interaction.invalid = Boolean(overlaps(item));
  renderCanvas(); renderInspector(); renderCode();
}

export function endCanvasInteraction() {
  if (!runtime.interaction) return;
  const item = state.elements.find(candidate => candidate.id === runtime.interaction.id);
  if (item && runtime.interaction.invalid) {
    Object.assign(item, runtime.interaction.initial);
    toast("Move rejected: elements cannot overlap unless overlap is enabled");
  } else if (snapshot() !== runtime.interaction.checkpoint) {
    runtime.undoStack.push(runtime.interaction.checkpoint);
    runtime.redoStack = [];
  }
  runtime.interaction = null;
  changed();
}

export function handleDrop(event) {
  event.preventDefault();
  $("#sequenceCanvas").classList.remove("drop-active");
  const kind = event.dataTransfer?.getData("text/pulseplot-kind");
  if (!kind) return;
  const point = pointerToSvg(event);
  const m = canvasMetrics();
  const channel = channelAtY(point.y, m);
  const time = (point.x - m.left) / m.xScale;
  addElement(kind, channel.id, time, { magnetic: true });
}

export function renderShapeDrag(event) {
  if (!runtime.shapeInteraction) return;
  const item = selected();
  const svg = $("#shapeEditor");
  if (!item || !svg) return;
  const point = pointerToSvg(event, svg), pad = 9;
  const x = clamp((point.x - pad) / (480 - pad * 2), 0, 1);
  const y = clamp((100 - pad - point.y) / (100 - pad * 2), 0, 1);
  const index = runtime.shapeInteraction.index;
  item.customPoints[index] = [index === 0 ? 0 : index === item.customPoints.length - 1 ? 1 : round(x, 3), round(y, 3)];
  item.customPoints.sort((a, b) => a[0] - b[0]);
  renderShapeEditor(item); renderCanvas(); renderCode();
}
