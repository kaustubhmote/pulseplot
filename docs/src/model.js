import { DEFAULT_FACE_COLOR, DEFAULT_EDGE_COLOR, DEFAULT_TEXT_COLOR, CHANNEL_Y_SPACING, defaults } from "./config.js";
import { deepCopy, uid, round, clamp, formatNum } from "./utils.js";
import { state } from "./state.js";
import { isRotorElement } from "./shapes.js";
import { snap } from "./snapping.js";

export function el(type, channel, start, duration, extra = {}) {
  return {
    id: uid("el"), type, channel, start, duration, amplitude: type === "delay" ? .45 : type === "marker" ? -.2 : .75,
    phase: "", text: "", shape: type === "shaped" ? "gauss" : type === "fid" ? "fid_5_5" : "",
    facecolor: DEFAULT_FACE_COLOR, edgecolor: DEFAULT_EDGE_COLOR, textcolor: DEFAULT_TEXT_COLOR,
    hatch: "", alpha: 1,
    truncateOff: false, tdx: 0, tdy: 0, tfs: 14, pdx: 0, pdy: 0, pfs: 14, allowOverlap: true,
    rotorInsetWidth: 1.5, rotorYOffset: .5,
    customPoints: [[0, 0], [.2, .3], [.5, 1], [.8, .3], [1, 0]], ...extra
  };
}

export function positionChannels(channels) {
  const highest = (channels.length - 1) * CHANNEL_Y_SPACING;
  channels.forEach((channel, index) => { channel.value = round(highest - index * CHANNEL_Y_SPACING); });
  return channels;
}

export function normalizeState(candidate) {
  const result = deepCopy(defaults);
  if (!candidate || typeof candidate !== "object") return result;
  result.settings = { ...result.settings, ...(candidate.settings || {}) };
  result.channels = positionChannels(Array.isArray(candidate.channels) && candidate.channels.length
    ? candidate.channels.map((channel, i) => ({ id: channel.id || uid("ch"), name: channel.name || `f${i + 1}`, value: 0 }))
    : result.channels);
  const channelIds = new Set(result.channels.map(channel => channel.id));
  result.elements = Array.isArray(candidate.elements) ? candidate.elements
    .filter(item => item && channelIds.has(item.channel))
    .map(item => {
      const normalized = { ...el(item.type || "pulse", item.channel, Number(item.start) || 0, Number(item.duration) || 0), ...item, id: item.id || uid("el") };
      normalized.facecolor = item.facecolor || item.color || DEFAULT_FACE_COLOR;
      normalized.edgecolor = item.edgecolor || DEFAULT_EDGE_COLOR;
      normalized.textcolor = item.textcolor || DEFAULT_TEXT_COLOR;
      normalized.hatch = String(item.hatch || "");
      normalized.alpha = clamp(Number.isFinite(Number(item.alpha)) ? Number(item.alpha) : 1, 0, 1);
      delete normalized.color;
      return normalized;
    }) : [];
  result.activeChannelId = channelIds.has(candidate.activeChannelId) ? candidate.activeChannelId : result.channels[0].id;
  const elementIds = new Set(result.elements.map(item => item.id));
  const requestedSelection = Array.isArray(candidate.selectedIds) ? candidate.selectedIds : candidate.selectedId ? [candidate.selectedId] : [];
  result.selectedIds = [...new Set(requestedSelection.filter(id => elementIds.has(id)))];
  result.selectedId = elementIds.has(candidate.selectedId)
    ? candidate.selectedId
    : result.selectedIds[result.selectedIds.length - 1] || null;
  if (result.selectedId && !result.selectedIds.includes(result.selectedId)) result.selectedIds.push(result.selectedId);
  return result;
}

export function snapshot() { return JSON.stringify({ settings: state.settings, channels: state.channels, elements: state.elements, selectedId: state.selectedId, selectedIds: state.selectedIds, activeChannelId: state.activeChannelId }); }

export function maxEnd() { return state.elements.reduce((max, item) => Math.max(max, item.start + Math.max(0, item.duration)), 0); }

export function selected() { return state.elements.find(item => item.id === state.selectedId) || null; }

export function selectedItems() {
  const ids = new Set(state.selectedIds || []);
  return state.elements.filter(item => ids.has(item.id));
}

export function setSelection(ids, primaryId = null) {
  const validIds = new Set(state.elements.map(item => item.id));
  state.selectedIds = [...new Set(ids)].filter(id => validIds.has(id));
  state.selectedId = primaryId && state.selectedIds.includes(primaryId)
    ? primaryId
    : state.selectedIds[state.selectedIds.length - 1] || null;
}

export function isElementSelected(id) { return (state.selectedIds || []).includes(id); }

export function overlaps(candidate, ignoreId = candidate.id) {
  if (candidate.allowOverlap || candidate.type === "marker" || isRotorElement(candidate)) return null;
  const a0 = candidate.start, a1 = candidate.start + candidate.duration;
  return state.elements.find(other => {
    if (other.id === ignoreId || other.channel !== candidate.channel || other.type === "marker" || isRotorElement(other)) return false;
    const b0 = other.start, b1 = other.start + other.duration;
    return a0 < b1 - 1e-8 && a1 > b0 + 1e-8;
  }) || null;
}

export function nextOpenStart(item) {
  let start = Math.max(0, snap(item.start));
  const occupied = state.elements.filter(other => other.channel === item.channel && other.type !== "marker" && !isRotorElement(other)).sort((a, b) => a.start - b.start);
  let moved = true;
  while (moved) {
    moved = false;
    for (const other of occupied) {
      if (start < other.start + other.duration && start + item.duration > other.start) {
        start = snap(other.start + other.duration);
        moved = true;
      }
    }
  }
  return start;
}

export function inferGapDelays(items, channelId) {
  const result = [];
  let cursor = null;
  items.forEach(item => {
    if (cursor !== null && item.start > cursor + 1e-8) {
      result.push({
        id: `auto-gap-${channelId}-${formatNum(cursor)}`,
        type: "delay", channel: channelId, start: cursor, duration: round(item.start - cursor),
        phase: "", text: "", tdx: 0, tdy: 0, tfs: 14, pdx: 0, pdy: 0, pfs: 14
      });
    }
    result.push(item);
    const end = item.start + Math.max(0, item.duration);
    cursor = cursor === null ? end : Math.max(cursor, end);
  });
  return result;
}

export function findChannelGaps(channelId) {
  const intervals = state.elements
    .filter(item => item.channel === channelId && item.type !== "marker" && !isRotorElement(item) && item.duration > 0)
    .map(item => ({ start: Math.max(0, item.start), end: Math.max(0, item.start + item.duration) }))
    .sort((a, b) => a.start - b.start || a.end - b.end);
  if (!intervals.length) return [];
  const gaps = [];
  let cursor = 0;
  intervals.forEach(interval => {
    if (interval.start > cursor + 1e-8) gaps.push({ start: round(cursor), duration: round(interval.start - cursor) });
    cursor = Math.max(cursor, interval.end);
  });
  return gaps.filter(gap => gap.duration > 1e-8);
}

export function validateState() {
  const problems = [];
  state.elements.forEach(item => {
    if (item.start < 0) problems.push(`${item.type} has a negative start time`);
    if (item.type !== "marker" && item.duration <= 0) problems.push(`${item.type} has a non-positive duration`);
    const conflict = overlaps(item);
    if (conflict && item.id.localeCompare(conflict.id) < 0) problems.push(`Overlap at t=${formatNum(Math.max(item.start, conflict.start))} on ${state.channels.find(c => c.id === item.channel)?.name}`);
  });
  return problems;
}
