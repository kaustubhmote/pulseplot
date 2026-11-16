import { DEFAULT_FACE_COLOR, DEFAULT_EDGE_COLOR, DEFAULT_TEXT_COLOR } from "./config.js";
import { deepCopy, uid } from "./utils.js";
import { state, setState, runtime } from "./state.js";
import { el, normalizeState, maxEnd, selected, selectedItems, setSelection, overlaps, nextOpenStart, findChannelGaps } from "./model.js";
import { isRotorElement } from "./shapes.js";
import { checkpoint } from "./history.js";
import { changed } from "./render.js";
import { canvasMetrics } from "./svg.js";
import { snap, magneticStart } from "./snapping.js";
import { toast } from "./notifications.js";
import { templates } from "./templates.js";

export function addElement(kind, channelId = state.activeChannelId, start = null, { magnetic = false } = {}) {
  checkpoint();
  const type = kind;
  const duration = type === "marker" ? 0 : type === "delay" ? 2 : type === "fid" ? 4 : type === "rotor" ? 1 : 1.5;
  const channelElements = state.elements.filter(item => item.channel === channelId && !isRotorElement(item));
  const defaultStart = channelElements.reduce((max, item) => Math.max(max, item.start + item.duration), 0);
  const rawStart = start === null ? defaultStart : Math.max(0, start);
  const item = el(type, channelId, snap(rawStart), duration, {
    shape: type === "shaped" ? "gauss" : type === "fid" ? "fid_5_5" : "",
    amplitude: type === "marker" ? -.2 : type === "delay" ? .45 : .75,
    facecolor: DEFAULT_FACE_COLOR,
    edgecolor: DEFAULT_EDGE_COLOR,
    textcolor: DEFAULT_TEXT_COLOR
  });
  if (magnetic) item.start = magneticStart(item, rawStart, canvasMetrics()).value;
  if (overlaps(item)) item.start = nextOpenStart(item);
  state.elements.push(item);
  setSelection([item.id], item.id);
  state.activeChannelId = channelId;
  if (item.start + item.duration > state.settings.timeRange) state.settings.timeRange = Math.ceil(item.start + item.duration + 2);
  changed();
  toast(`${type === "fid" ? "FID" : type[0].toUpperCase() + type.slice(1)} added`);
}

export function deleteSelected() {
  const items = selectedItems();
  if (!items.length) return;
  checkpoint();
  const ids = new Set(items.map(item => item.id));
  state.elements = state.elements.filter(item => !ids.has(item.id));
  setSelection([]);
  changed();
}

export function duplicateSelected() {
  const items = selectedItems();
  if (!items.length) return;
  checkpoint();
  const minStart = Math.min(...items.map(item => item.start));
  const maxEnd = Math.max(...items.map(item => item.start + Math.max(0, item.duration)));
  const shift = Math.max(state.settings.snap, maxEnd - minStart + state.settings.snap);
  const clones = items.map(item => ({ ...deepCopy(item), id: uid("el"), start: snap(item.start + shift) }));
  clones.forEach(clone => { if (overlaps(clone)) clone.start = nextOpenStart(clone); state.elements.push(clone); });
  setSelection(clones.map(clone => clone.id), clones[clones.length - 1].id);
  state.activeChannelId = clones[clones.length - 1].channel;
  changed();
  toast(`${clones.length} element${clones.length === 1 ? "" : "s"} duplicated`);
}

export function copySelected() {
  const item = selected();
  if (!item) return;
  runtime.copiedElement = deepCopy(item);
  toast(`${item.type[0].toUpperCase() + item.type.slice(1)} copied`);
}

export function pasteCopied() {
  if (!runtime.copiedElement) return;
  checkpoint();
  const clone = {
    ...deepCopy(runtime.copiedElement),
    id: uid("el"),
    channel: runtime.pasteTarget?.channel || state.activeChannelId,
    start: runtime.pasteTarget ? Math.max(0, snap(runtime.pasteTarget.start)) : snap(runtime.copiedElement.start + Math.max(state.settings.snap, runtime.copiedElement.duration))
  };
  state.elements.push(clone);
  setSelection([clone.id], clone.id);
  state.activeChannelId = clone.channel;
  changed();
  toast(`${clone.type[0].toUpperCase() + clone.type.slice(1)} pasted`);
}

export function fillDelays() {
  const delays = state.channels.flatMap(channel => findChannelGaps(channel.id).map(gap =>
    el("delay", channel.id, gap.start, gap.duration, { text: "", allowOverlap: true })
  ));
  if (!delays.length) {
    toast("No empty intervals to fill");
    return;
  }
  checkpoint();
  state.elements.push(...delays);
  setSelection(delays.map(delay => delay.id), delays[0].id);
  state.activeChannelId = delays[0].channel;
  changed();
  toast(`${delays.length} delay${delays.length === 1 ? "" : "s"} added`);
}

export function loadTemplate(name) {
  if (state.elements.length && !confirm("Replace the current workspace with this template?")) return;
  checkpoint();
  const currentTheme = state.settings.theme;
  setState(normalizeState(deepCopy(templates[name])));
  state.settings.theme = currentTheme;
  changed();
  toast("Template loaded");
}
