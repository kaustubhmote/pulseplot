import { NS } from "./config.js";
import { $, clamp } from "./utils.js";
import { state } from "./state.js";
import { supportsPatchStyle } from "./shapes.js";

export function svgEl(name, attrs = {}, text = null) {
  const node = document.createElementNS(NS, name);
  Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
  if (text !== null) node.textContent = text;
  return node;
}

export function hatchPattern(defs, item) {
  const hatch = String(item.hatch || "");
  if (!hatch || !supportsPatchStyle(item)) return null;
  const size = clamp(10 - (hatch.length - 1) * 1.5, 4, 10);
  const id = `hatch-${String(item.id).replace(/[^A-Za-z0-9_-]/g, "-")}`;
  const pattern = svgEl("pattern", { id, width: size, height: size, patternUnits: "userSpaceOnUse" });
  const characters = new Set(hatch);
  const paths = [];
  if (characters.has("/") || characters.has("x") || characters.has("*")) paths.push(`M -2 ${size} L ${size} -2 M 0 ${size + 2} L ${size + 2} 0`);
  if (characters.has("\\") || characters.has("x") || characters.has("*")) paths.push(`M -2 0 L ${size} ${size + 2} M 0 -2 L ${size + 2} ${size}`);
  if (characters.has("|") || characters.has("+") || characters.has("*")) paths.push(`M ${size / 2} 0 V ${size}`);
  if (characters.has("-") || characters.has("+") || characters.has("*")) paths.push(`M 0 ${size / 2} H ${size}`);
  paths.forEach(d => pattern.append(svgEl("path", { d, fill: "none", stroke: item.edgecolor, "stroke-width": 1.1 })));
  if (characters.has(".")) pattern.append(svgEl("circle", { cx: size / 2, cy: size / 2, r: .9, fill: item.edgecolor }));
  if (characters.has("o") || characters.has("O")) pattern.append(svgEl("circle", { cx: size / 2, cy: size / 2, r: characters.has("O") ? size * .3 : size * .2, fill: "none", stroke: item.edgecolor, "stroke-width": 1 }));
  defs.append(pattern);
  return `url(#${id})`;
}

export function canvasMetrics({ width = null, height = null } = {}) {
  const resolvedWidth = width ?? Math.max(820, $("#canvasShell").clientWidth || 820);
  const left = 104, right = 28, top = 48, bottom = 34;
  const resolvedHeight = height ?? top + bottom + state.channels.length * state.settings.channelSpacing;
  const channelSpacing = (resolvedHeight - top - bottom) / Math.max(1, state.channels.length);
  const plotWidth = resolvedWidth - left - right;
  return { width: resolvedWidth, height: resolvedHeight, left, right, top, bottom, channelSpacing, plotWidth, xScale: plotWidth / Math.max(1, state.settings.timeRange) };
}

export function channelAtY(y, metrics = canvasMetrics()) {
  const index = clamp(Math.floor((y - metrics.top) / metrics.channelSpacing), 0, state.channels.length - 1);
  return state.channels[index];
}

export function channelY(channelId, metrics = canvasMetrics()) {
  const index = Math.max(0, state.channels.findIndex(channel => channel.id === channelId));
  return metrics.top + index * metrics.channelSpacing + metrics.channelSpacing / 2;
}

export function chooseGridStep(range) {
  if (range <= 10) return 1;
  if (range <= 30) return 2;
  if (range <= 70) return 5;
  return 10;
}
