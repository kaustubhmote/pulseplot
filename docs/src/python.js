import { clamp, formatNum } from "./utils.js";
import { state } from "./state.js";
import { inferGapDelays } from "./model.js";
import { parseShape, isShapedElement, isRotorElement, supportsPatchStyle } from "./shapes.js";

export function pulseToken(item, includeShape = true, colorAliases = {}) {
  const channel = state.channels.find(c => c.id === item.channel);
  const parts = [item.type === "delay" ? `d=${formatNum(item.duration)}` : `p=${formatNum(item.type === "marker" ? 0 : item.duration)}`];
  if (item.type !== "delay") parts.push(`pl=${formatNum(item.amplitude)}`);
  parts.push(`f=${formatNum(channel?.value ?? 0)}`, `st=${formatNum(item.start)}`);
  if (item.phase.trim()) parts.push(`ph=${safeToken(item.phase)}`);
  if (item.text.trim()) parts.push(`tx=\`${safeText(item.text)}\``);
  if (item.tdx) parts.push(`tdx=${formatNum(item.tdx)}`);
  if (item.tdy) parts.push(`tdy=${formatNum(item.tdy)}`);
  if (item.tfs !== 14) parts.push(`tfs=${formatNum(item.tfs)}`);
  if (item.pdx) parts.push(`pdx=${formatNum(item.pdx)}`);
  if (item.pdy) parts.push(`pdy=${formatNum(item.pdy)}`);
  if (item.pfs !== 14) parts.push(`pfs=${formatNum(item.pfs)}`);
  if (supportsPatchStyle(item)) {
    const alpha = clamp(Number.isFinite(Number(item.alpha)) ? Number(item.alpha) : 1, 0, 1);
    if (alpha !== 1) parts.push(`al=${formatNum(alpha)}`);
    if (String(item.hatch || "").trim()) parts.push(`h=${safeToken(item.hatch)}`);
  }
  if (includeShape && isShapedElement(item) && item.shape) parts.push(`sp=${safeToken(item.shape)}`);
  if (isShapedElement(item) && (item.truncateOff || ["fid", "fid2"].includes(parseShape(item.shape).name))) parts.push("troff");
  if (colorAliases.face && item.type !== "delay") parts.push(`fc_${colorAliases.face}`);
  if (colorAliases.edge && item.type !== "delay") parts.push(`ec_${colorAliases.edge}`);
  return parts.join(" ");
}

export function safeToken(value) { return String(value).trim().replace(/\s+/g, "_").replace(/[`#]/g, ""); }

export function safeText(value) { return String(value).replace(/`/g, "'").replace(/\r?\n/g, " ").replace(/#/g, "＃"); }

export function pyList(values) { return `[${values.map(value => formatNum(value)).join(", ")}]`; }

export function isCustomShape(item) { return isShapedElement(item) && ["custom", "sinc"].includes(parseShape(item.shape).name); }

export function isDefaultFaceColor(value) { return ["#ffffff", "white"].includes(String(value).toLowerCase()); }

export function isDefaultEdgeColor(value) { return ["#000000", "black"].includes(String(value).toLowerCase()); }

export function generatePython() {
  const needsNumpy = state.elements.some(isCustomShape);
  const lines = ["import pulseplot as pplot", "import matplotlib.pyplot as plt"];
  if (needsNumpy) lines.push("import numpy as np");
  lines.push("", `fig, ax = pplot.subplots(`, `    figsize=(${formatNum(state.settings.figureWidth)}, ${formatNum(state.settings.figureHeight)}),`, ")");
  lines.push(`ax.fontsize = ${formatNum(state.settings.fontSize)}`, "");

  const channelOrder = new Map(state.channels.map((channel, index) => [channel.id, index]));
  const rotors = state.elements.filter(isRotorElement).sort((a, b) => a.start - b.start || channelOrder.get(a.channel) - channelOrder.get(b.channel));
  const items = state.channels.flatMap(channel => {
    const channelItems = state.elements.filter(item => item.channel === channel.id && !isRotorElement(item)).sort((a, b) => a.start - b.start);
    return inferGapDelays(channelItems, channel.id);
  });
  items.sort((a, b) => a.start - b.start || channelOrder.get(a.channel) - channelOrder.get(b.channel));

  const standard = items.filter(item => !isCustomShape(item));
  const custom = items.filter(isCustomShape);
  const colorAliases = new Map();
  standard.filter(item => item.type !== "delay").forEach((item, colorIndex) => {
    const aliases = {};
    if (!isDefaultFaceColor(item.facecolor)) aliases.face = `face_${colorIndex}`;
    if (!isDefaultEdgeColor(item.edgecolor)) aliases.edge = `edge_${colorIndex}`;
    if (aliases.face || aliases.edge) colorAliases.set(item.id, aliases);
  });

  state.channels.forEach((channel, index) => lines.push(`# Channel ${index + 1}: ${channel.name.replace(/\n/g, " ")}`));
  standard.filter(item => colorAliases.has(item.id)).forEach(item => {
    const aliases = colorAliases.get(item.id);
    if (aliases.face) lines.push(`ax.params["fc_${aliases.face}"] = ${pythonQuote(item.facecolor)}`);
    if (aliases.edge) lines.push(`ax.params["ec_${aliases.edge}"] = ${pythonQuote(item.edgecolor)}`);
  });
  if (standard.length) {
    lines.push("", `ax.pseq(r"""`);
    standard.forEach(item => lines.push(pulseToken(item, true, colorAliases.get(item.id) || {})));
    lines.push('""")');
  }
  custom.forEach(item => {
    let shape;
    const parsedShape = parseShape(item.shape);
    if (parsedShape.name === "sinc") shape = `lambda x: np.abs(np.sinc(${formatNum(parsedShape.params[0])} * (x - 0.5)))`;
    else {
      const points = [...item.customPoints].sort((a, b) => a[0] - b[0]);
      shape = `lambda x: np.interp(x, ${pyList(points.map(point => point[0]))}, ${pyList(points.map(point => point[1]))})`;
    }
    const styleArgs = [];
    if (!isDefaultFaceColor(item.facecolor)) styleArgs.push(`facecolor=${pythonQuote(item.facecolor)}`);
    if (!isDefaultEdgeColor(item.edgecolor)) styleArgs.push(`edgecolor=${pythonQuote(item.edgecolor)}`);
    lines.push(`ax.pulse(r"${pythonRawString(pulseToken(item, false))}", shape=${shape}${styleArgs.length ? `, ${styleArgs.join(", ")}` : ""})`);
  });
  lines.push("");
  lines.push(`ax.draw_channels(${state.channels.map(channel => formatNum(channel.value)).join(", ")})`);
  lines.push(`ax.set_xlim(0, ${formatNum(state.settings.timeRange)})`);
  lines.push("");
  if (state.settings.title) lines.push(`fig.suptitle(${pythonQuote(state.settings.title)}, fontsize=${formatNum(state.settings.fontSize + 2)})`);
  lines.push("plt.tight_layout()");
  rotors.forEach(item => {
    const channel = state.channels.find(candidate => candidate.id === item.channel);
    const center = item.start + item.duration / 2;
    lines.push(`ax.rotor(axdims=[${formatNum(center)}, ${formatNum((channel?.value ?? 0) + item.rotorYOffset)}, ${formatNum(item.rotorInsetWidth)}], length=${formatNum(item.duration)})`);
  });
  lines.push('plt.savefig("pulse_sequence.png", dpi=300)', "plt.show()", "");
  return lines.join("\n");
}

export function pythonQuote(value) { return JSON.stringify(String(value)).replace(/\\u2028|\\u2029/g, ""); }

export function pythonRawString(value) { return String(value).replace(/"/g, '\\"').replace(/\r?\n/g, " "); }

export function highlightPython(code) {
  const escaped = code.replace(/[&<>]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[char]));
  const stash = [];
  let tokenized = escaped.replace(/(r?"""[\s\S]*?"""|r?"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')/g, match => {
    stash.push(`<span class="tok-str">${match}</span>`);
    return `\u0000${"x".repeat(stash.length)}\u0000`;
  });
  tokenized = tokenized.replace(/(^|\s)(#.*)$/gm, (_, lead, comment) => `${lead}<span class="tok-comment">${comment}</span>`);
  tokenized = tokenized.replace(/\b(import|as|from|lambda)\b/g, '<span class="tok-key">$1</span>');
  tokenized = tokenized.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="tok-num">$1</span>');
  tokenized = tokenized.replace(/\b(pplot|plt|pseq|pulse|rotor|draw_channels|set_title|set_xlim|grid|savefig|show|tight_layout|interp|sinc)\b/g, '<span class="tok-fn">$1</span>');
  return tokenized.replace(/\u0000(x+)\u0000/g, (_, marker) => stash[marker.length - 1]);
}
