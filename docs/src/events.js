import { SHAPE_SPECS } from "./config.js";
import { $, $$, deepCopy, uid, clamp } from "./utils.js";
import { state, setState, runtime } from "./state.js";
import { positionChannels, normalizeState, snapshot, maxEnd, selected, setSelection, isElementSelected, overlaps } from "./model.js";
import { parseShape, composeShape } from "./shapes.js";
import { checkpoint, undo, redo, updateUndoButtons } from "./history.js";
import { changed, queueRender, renderAll } from "./render.js";
import { canvasMetrics, channelAtY } from "./svg.js";
import { snap } from "./snapping.js";
import { applyBatchControl } from "./inspector.js";
import { addElement, deleteSelected, duplicateSelected, copySelected, pasteCopied, fillDelays, loadTemplate } from "./commands.js";
import { generatePython } from "./python.js";
import { pointerToSvg, beginCanvasInteraction, moveCanvasInteraction, endCanvasInteraction, handleDrop, renderShapeDrag } from "./interactions.js";
import { download, cleanSvgString, exportPng } from "./exports.js";
import { toast } from "./notifications.js";

export function bindEvents() {
  $("#addChannelBtn").addEventListener("click", () => {
    checkpoint();
    const number = state.channels.length + 1;
    const channel = { id: uid("ch"), name: `f${number}`, value: 0 };
    state.channels.push(channel); positionChannels(state.channels); state.activeChannelId = channel.id; changed();
  });

  $("#channelList").addEventListener("focusin", event => {
    if (event.target.matches("[data-channel-name]")) event.target.dataset.before = snapshot();
  });
  $("#channelList").addEventListener("input", event => {
    const row = event.target.closest("[data-channel-id]");
    if (!row || !event.target.matches("[data-channel-name]")) return;
    const channel = state.channels.find(item => item.id === row.dataset.channelId);
    if (channel) {
      channel.name = event.target.value;
      changed({ inspector: false });
    }
  });
  $("#channelList").addEventListener("change", event => {
    const row = event.target.closest("[data-channel-id]");
    if (row) state.activeChannelId = row.dataset.channelId;
    const before = event.target.dataset.before;
    if (before && before !== snapshot()) { runtime.undoStack.push(before); runtime.redoStack = []; updateUndoButtons(); }
  });
  $("#channelList").addEventListener("click", event => {
    const row = event.target.closest("[data-channel-id]");
    if (!row) return;
    state.activeChannelId = row.dataset.channelId;
    if (event.target.matches("[data-remove-channel]")) {
      if (state.channels.length === 1) return;
      const count = state.elements.filter(item => item.channel === row.dataset.channelId).length;
      if (count && !confirm(`Remove this channel and its ${count} element${count === 1 ? "" : "s"}?`)) return;
      checkpoint();
      state.channels = state.channels.filter(item => item.id !== row.dataset.channelId);
      positionChannels(state.channels);
      state.elements = state.elements.filter(item => item.channel !== row.dataset.channelId);
      state.activeChannelId = state.channels[0].id;
      setSelection((state.selectedIds || []).filter(id => state.elements.some(item => item.id === id)), state.selectedId);
    }
    changed();
  });

  $$(".palette-item").forEach(item => {
    item.addEventListener("dragstart", event => { event.dataTransfer.setData("text/pulseplot-kind", item.dataset.kind); event.dataTransfer.effectAllowed = "copy"; });
    item.addEventListener("click", () => addElement(item.dataset.kind));
    item.addEventListener("keydown", event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); addElement(item.dataset.kind); } });
  });

  $("#settingsForm").addEventListener("focusin", event => { if (event.target.matches("[data-setting]")) event.target.dataset.before = snapshot(); });
  $("#settingsForm").addEventListener("input", event => {
    const input = event.target;
    if (!input.matches("[data-setting]")) return;
    const key = input.dataset.setting;
    state.settings[key] = input.type === "checkbox" ? input.checked : input.type === "number" ? Number(input.value) : input.value;
    changed({ inspector: false });
  });
  $("#settingsForm").addEventListener("change", event => {
    const before = event.target.dataset.before;
    if (before && before !== snapshot()) { runtime.undoStack.push(before); runtime.redoStack = []; }
    updateUndoButtons();
  });

  const svg = $("#sequenceCanvas");
  svg.addEventListener("pointerdown", beginCanvasInteraction);
  svg.addEventListener("pointermove", moveCanvasInteraction);
  svg.addEventListener("pointerup", endCanvasInteraction);
  svg.addEventListener("pointercancel", endCanvasInteraction);
  svg.addEventListener("click", event => {
    const group = event.target.closest("[data-element-id]");
    if (group) {
      const id = group.dataset.elementId;
      const additive = event.ctrlKey || event.metaKey;
      if (additive) {
        const ids = new Set(state.selectedIds || []);
        if (ids.has(id)) ids.delete(id); else ids.add(id);
        setSelection([...ids], ids.has(id) ? id : null);
      } else if (!isElementSelected(id)) {
        setSelection([id], id);
      }
      const item = state.elements.find(candidate => candidate.id === id);
      if (item) state.activeChannelId = item.channel;
    }
    else {
      const point = pointerToSvg(event), metrics = canvasMetrics();
      const channel = channelAtY(point.y, metrics);
      setSelection([]);
      state.activeChannelId = channel.id;
      runtime.pasteTarget = { channel: channel.id, start: (point.x - metrics.left) / metrics.xScale };
    }
    renderAll();
  });
  svg.addEventListener("dragover", event => { event.preventDefault(); event.dataTransfer.dropEffect = "copy"; svg.classList.add("drop-active"); });
  svg.addEventListener("dragleave", () => svg.classList.remove("drop-active"));
  svg.addEventListener("drop", handleDrop);

  $("#inspector").addEventListener("focusin", event => {
    if (event.target.matches("[data-prop], [data-batch-prop], [data-shape-name], [data-shape-param]")) event.target.dataset.before = snapshot();
  });
  $("#inspector").addEventListener("input", event => {
    const item = selected();
    if (!item) return;
    if (event.target.matches("[data-batch-prop]")) {
      applyBatchControl(event.target);
      return;
    }
    if (event.target.matches("[data-shape-param]")) {
      const parsed = parseShape(item.shape);
      parsed.params[Number(event.target.dataset.shapeParam)] = Number(event.target.value);
      item.shape = composeShape(parsed.name, parsed.params);
      const preview = $("[data-shape-preview]", $("#inspector"));
      if (preview) preview.value = item.shape;
      changed({ inspector: false });
      return;
    }
    if (!event.target.matches("[data-prop]")) return;
    const key = event.target.dataset.prop;
    const previous = item[key];
    const value = event.target.type === "checkbox" ? event.target.checked : event.target.type === "number" ? Number(event.target.value) : event.target.value;
    item[key] = key === "alpha" ? clamp(Number.isFinite(value) ? value : 1, 0, 1) : value;
    if (key === "alpha") event.target.value = item.alpha;
    if (overlaps(item)) {
      item[key] = previous;
      event.target.value = previous;
      event.target.checked = Boolean(previous);
      toast("Change rejected because it would overlap another element");
    }
    if (key === "channel") state.activeChannelId = item.channel;
    changed({ inspector: false });
  });
  $("#inspector").addEventListener("change", event => {
    const item = selected();
    const before = event.target.dataset.before;
    if (event.target.matches("[data-batch-prop]")) {
      applyBatchControl(event.target);
      if (before && before !== snapshot()) { runtime.undoStack.push(before); runtime.redoStack = []; }
      updateUndoButtons();
      changed();
      return;
    }
    if (item && event.target.matches("[data-shape-name]")) {
      const name = event.target.value;
      item.shape = composeShape(name, SHAPE_SPECS[name].params.map(parameter => parameter.default));
      if (before && before !== snapshot()) { runtime.undoStack.push(before); runtime.redoStack = []; }
      updateUndoButtons();
      changed();
      return;
    }
    if (item && event.target.matches("[data-shape-param]")) {
      const parsed = parseShape(item.shape);
      parsed.params[Number(event.target.dataset.shapeParam)] = Number(event.target.value);
      item.shape = composeShape(parsed.name, parsed.params);
      if (before && before !== snapshot()) { runtime.undoStack.push(before); runtime.redoStack = []; }
      updateUndoButtons();
      changed();
      return;
    }
    if (item && event.target.matches("[data-prop]")) {
      const key = event.target.dataset.prop;
      const value = event.target.type === "checkbox" ? event.target.checked : event.target.type === "number" ? Number(event.target.value) : event.target.value;
      item[key] = key === "alpha" ? clamp(Number.isFinite(value) ? value : 1, 0, 1) : value;
    }
    if (before && before !== snapshot()) { runtime.undoStack.push(before); runtime.redoStack = []; }
    updateUndoButtons();
  });
  $("#inspector").addEventListener("click", event => {
    const action = event.target.dataset.inspectorAction;
    if (action === "delete") { deleteSelected(); return; }
    if (action === "duplicate") { duplicateSelected(); return; }
    const tile = event.target.closest(".inspector-grid .field");
    if (!tile || event.target.matches("input, select, textarea, button")) return;
    tile.querySelector("input:not(:disabled), select:not(:disabled), textarea:not(:disabled)")?.focus();
  });
  $("#inspector").addEventListener("pointerdown", event => {
    const point = event.target.closest("[data-point-index]");
    if (!point) return;
    event.preventDefault();
    runtime.shapeInteraction = { index: Number(point.dataset.pointIndex), before: snapshot() };
    $("#shapeEditor").setPointerCapture(event.pointerId);
  });
  $("#inspector").addEventListener("pointermove", renderShapeDrag);
  $("#inspector").addEventListener("pointerup", () => {
    if (!runtime.shapeInteraction) return;
    if (runtime.shapeInteraction.before !== snapshot()) { runtime.undoStack.push(runtime.shapeInteraction.before); runtime.redoStack = []; }
    runtime.shapeInteraction = null; changed();
  });

  $("#loadTemplateBtn").addEventListener("click", () => loadTemplate($("#templateSelect").value));
  $("#fitBtn").addEventListener("click", () => {
    checkpoint(); state.settings.timeRange = Math.max(5, Math.ceil(maxEnd() + 2)); changed();
  });
  $("#fillDelaysBtn").addEventListener("click", fillDelays);
  $("#clearBtn").addEventListener("click", () => {
    if (state.elements.length && !confirm("Clear every element from the canvas?")) return;
    checkpoint(); state.elements = []; setSelection([]); changed();
  });
  $("#undoBtn").addEventListener("click", undo);
  $("#redoBtn").addEventListener("click", redo);
  $("#themeBtn").addEventListener("click", () => { state.settings.theme = state.settings.theme === "dark" ? "light" : "dark"; changed(); });
  $("#codeToggleBtn").addEventListener("click", () => {
    const card = $("#codeCard");
    const collapsed = card.classList.toggle("collapsed");
    $("#codeToggleBtn").textContent = collapsed ? "Expand" : "Collapse";
    $("#codeToggleBtn").setAttribute("aria-expanded", String(!collapsed));
  });

  $("#copyCodeBtn").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(generatePython()); toast("Python copied to clipboard"); }
    catch { toast("Clipboard unavailable; select the code manually"); }
  });
  $("#downloadCodeBtn").addEventListener("click", () => download("pulse_sequence.py", new Blob([generatePython()], { type: "text/x-python;charset=utf-8" })));
  $("#exportSvgBtn").addEventListener("click", () => { download("pulse_sequence.svg", new Blob([cleanSvgString()], { type: "image/svg+xml;charset=utf-8" })); toast("SVG exported"); });
  $("#exportPngBtn").addEventListener("click", exportPng);
  $("#exportJsonBtn").addEventListener("click", () => download("pulseplot-project.json", new Blob([JSON.stringify(JSON.parse(snapshot()), null, 2)], { type: "application/json" })));
  $("#importBtn").addEventListener("click", () => $("#projectFile").click());
  $("#projectFile").addEventListener("change", async event => {
    const file = event.target.files[0]; if (!file) return;
    try { checkpoint(); setState(normalizeState(JSON.parse(await file.text()))); changed(); toast("Project imported"); }
    catch { toast("That file is not a valid pulseplot project"); }
    event.target.value = "";
  });

  window.addEventListener("resize", () => queueRender(false));
  document.addEventListener("keydown", event => {
    const typing = /INPUT|SELECT|TEXTAREA/.test(document.activeElement?.tagName);
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "z") { event.preventDefault(); event.shiftKey ? redo() : undo(); return; }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "y") { event.preventDefault(); redo(); return; }
    if (!typing && (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "d") { event.preventDefault(); duplicateSelected(); return; }
    if (!typing && (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "c") { event.preventDefault(); copySelected(); return; }
    if (!typing && (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "v") { event.preventDefault(); pasteCopied(); return; }
    if (typing) return;
    const item = selected();
    if ((event.key === "Delete" || event.key === "Backspace") && item) { event.preventDefault(); deleteSelected(); return; }
    if (!item || !["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) return;
    event.preventDefault(); checkpoint();
    const original = deepCopy(item);
    if (event.key === "ArrowLeft") item.start = Math.max(0, snap(item.start - state.settings.snap));
    if (event.key === "ArrowRight") item.start = snap(item.start + state.settings.snap);
    if (event.key === "ArrowUp" || event.key === "ArrowDown") {
      const index = state.channels.findIndex(channel => channel.id === item.channel);
      const next = clamp(index + (event.key === "ArrowUp" ? -1 : 1), 0, state.channels.length - 1);
      item.channel = state.channels[next].id; state.activeChannelId = item.channel;
    }
    if (overlaps(item)) { Object.assign(item, original); runtime.undoStack.pop(); toast("Move rejected because it would overlap another element"); }
    changed();
  });
}
