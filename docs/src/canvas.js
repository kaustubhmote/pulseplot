import { NS } from "./config.js";
import { $, clamp, formatNum } from "./utils.js";
import { state, runtime } from "./state.js";
import { isElementSelected } from "./model.js";
import { parseShape, isShapedElement, isRotorElement, supportsPatchStyle, shapeValues } from "./shapes.js";
import { displayMath } from "./math.js";
import { svgEl, hatchPattern, canvasMetrics, channelY, chooseGridStep } from "./svg.js";
import { snap } from "./snapping.js";

export function renderCanvas({ clean = false } = {}) {
  const svg = clean ? svgEl("svg") : $("#sequenceCanvas");
  const m = clean
    ? canvasMetrics({ width: state.settings.figureWidth * 96, height: state.settings.figureHeight * 96 })
    : canvasMetrics();
  svg.replaceChildren();
  svg.setAttribute("xmlns", NS);
  svg.setAttribute("viewBox", `0 0 ${m.width} ${m.height}`);
  svg.setAttribute("width", m.width);
  svg.setAttribute("height", m.height);
  svg.setAttribute("preserveAspectRatio", "xMinYMin meet");
  svg.style.background = clean ? "#ffffff" : "transparent";
  const defs = svgEl("defs");
  svg.append(defs);

  const styles = getComputedStyle(document.documentElement);
  const textColor = clean ? "#172033" : styles.getPropertyValue("--text").trim();
  const muted = clean ? "#667085" : styles.getPropertyValue("--muted").trim();
  const border = clean ? "#d7dde6" : styles.getPropertyValue("--border").trim();
  const grid = clean ? "#e8edf3" : styles.getPropertyValue("--border-soft").trim();
  const selectedColor = styles.getPropertyValue("--accent-2").trim();

  if (clean) svg.append(svgEl("rect", { x: 0, y: 0, width: m.width, height: m.height, fill: "#ffffff" }));
  svg.append(svgEl("title", {}, state.settings.title));
  if (state.settings.title) svg.append(svgEl("text", { x: m.left, y: 25, fill: textColor, "font-family": "system-ui, sans-serif", "font-weight": 700, "font-size": 16 }, state.settings.title));

  if (state.settings.grid) {
    const step = chooseGridStep(state.settings.timeRange);
    for (let t = 0; t <= state.settings.timeRange + 1e-8; t += step) {
      const x = m.left + t * m.xScale;
      svg.append(svgEl("line", { x1: x, y1: m.top - 10, x2: x, y2: m.height - m.bottom, stroke: grid, "stroke-width": t === 0 ? 1.5 : 1, "stroke-dasharray": t === 0 ? "" : "3 5" }));
      svg.append(svgEl("text", { x, y: m.height - 11, fill: muted, "text-anchor": "middle", "font-size": 10, "font-family": "system-ui, sans-serif" }, formatNum(t)));
    }
  }

  state.channels.forEach(channel => {
    const y = channelY(channel.id, m);
    const active = channel.id === state.activeChannelId;
    if (!clean && active) svg.append(svgEl("rect", { x: 0, y: y - m.channelSpacing / 2 + 3, width: m.width, height: m.channelSpacing - 6, fill: border, opacity: .12 }));
    svg.append(svgEl("line", { x1: m.left, y1: y, x2: m.width - m.right, y2: y, stroke: clean ? "#667085" : border, "stroke-width": 1.3 }));
    if (state.settings.labels) {
      svg.append(svgEl("rect", { x: 13, y: y - 16, width: 74, height: 32, rx: 8, fill: clean ? "#f4f6f8" : "transparent", stroke: clean ? "#d7dde6" : border }));
      svg.append(svgEl("circle", { cx: 24, cy: y, r: 4, fill: clean ? "#667085" : muted }));
      svg.append(svgEl("text", { x: 34, y: y + 4, fill: textColor, "font-size": 11, "font-family": "system-ui, sans-serif" }, channel.name));
    }
  });

  [...state.elements].sort((a, b) => Number(isRotorElement(a)) - Number(isRotorElement(b)) || a.start - b.start).forEach(item => {
    const channel = state.channels.find(c => c.id === item.channel);
    if (!channel) return;
    const y = channelY(item.channel, m);
    const x = m.left + item.start * m.xScale;
    const w = Math.max(item.type === "marker" ? 1 : 3, item.duration * m.xScale);
    const h = clamp(item.amplitude, -1.5, 1.5) * 58;
    const isSelected = !clean && isElementSelected(item.id);
    const group = svgEl("g", { "data-element-id": item.id, "data-element-type": item.type, tabindex: clean ? -1 : 0, role: clean ? "img" : "button", "aria-label": `${item.type} at ${formatNum(item.start)}` });
    const patchTarget = supportsPatchStyle(item) ? svgEl("g", { opacity: clamp(Number(item.alpha), 0, 1) }) : group;
    const hatchFill = hatchPattern(defs, item);
    group.style.cursor = clean ? "default" : "move";

    if (item.type === "delay") {
      // Delays are gaps on the existing channel baseline. The transparent
      // hit area keeps an unlabelled delay selectable without drawing it.
      if (!clean) group.append(svgEl("rect", { x, y: y - 13, width: w, height: 26, fill: "transparent", class: "delay-hit" }));
    } else if (item.type === "marker") {
      const markerTop = Math.min(y, y - h), markerBottom = Math.max(y, y - h);
      group.append(svgEl("line", { x1: x, y1: y, x2: x, y2: y - h, stroke: item.edgecolor, "stroke-width": 2 }));
      group.append(svgEl("rect", { x: x - 7, y: markerTop - 8, width: 14, height: Math.max(16, markerBottom - markerTop + 16), fill: "transparent" }));
    } else if (isRotorElement(item)) {
      const rotorRadius = clamp(item.duration * .1 * 18, 7, 24);
      const rotorCenterX = x + w / 2;
      const rotorCenterY = y - item.rotorYOffset * 58;
      const rotor = svgEl("g", { transform: `rotate(-54.7 ${rotorCenterX} ${rotorCenterY})` });
      rotor.append(svgEl("rect", { x, y: rotorCenterY - rotorRadius, width: w, height: rotorRadius * 2, rx: rotorRadius, fill: "#d8dde6", stroke: item.edgecolor, "stroke-width": 1.5 }));
      rotor.append(svgEl("rect", { x: x + w * .08, y: rotorCenterY - rotorRadius, width: Math.max(3, w * .1), height: rotorRadius * 2, fill: "#aeb7c5" }));
      rotor.append(svgEl("line", { x1: x + w * .82, y1: rotorCenterY - rotorRadius, x2: x + w * .82, y2: rotorCenterY + rotorRadius, stroke: "#8d97a7", "stroke-width": 2 }));
      group.append(rotor);
    } else if (isShapedElement(item)) {
      const points = shapeValues(item);
      const shapeName = parseShape(item.shape).name;
      const truncated = item.truncateOff || shapeName === "fid" || shapeName === "fid2";
      const path = [];
      if (truncated) {
        points.forEach(([px, py], index) => path.push(`${index ? "L" : "M"} ${x + px * w} ${y - py * h}`));
      } else {
        path.push(`M ${x} ${y}`);
        points.forEach(([px, py]) => path.push(`L ${x + px * w} ${y - py * h}`));
        path.push(`L ${x + w} ${y} Z`);
      }
      const d = path.join(" ");
      patchTarget.append(svgEl("path", { d, fill: truncated ? "none" : item.facecolor, stroke: item.edgecolor, "stroke-width": 1.6 }));
      if (hatchFill && !truncated) patchTarget.append(svgEl("path", { d, fill: hatchFill, stroke: "none" }));
    } else {
      const rect = { x, y: Math.min(y, y - h), width: w, height: Math.abs(h), rx: 2 };
      patchTarget.append(svgEl("rect", { ...rect, fill: item.facecolor, stroke: item.edgecolor, "stroke-width": 1.6 }));
      if (hatchFill) patchTarget.append(svgEl("rect", { ...rect, fill: hatchFill, stroke: "none" }));
    }

    if (patchTarget !== group) group.append(patchTarget);

    const fontSize = item.tfs || state.settings.fontSize;
    const elementTextColor = item.type === "pulse" || item.type === "marker" || isShapedElement(item) ? item.textcolor : textColor;
    if (item.text) group.append(svgEl("text", { x: x + w / 2 + item.tdx * m.xScale, y: y - h / 2 - item.tdy * 18, fill: elementTextColor, "font-size": fontSize, "font-family": "system-ui, sans-serif", "text-anchor": "middle", "pointer-events": "none" }, displayMath(item.text)));
    if (item.phase) {
      const phaseText = item.phase.startsWith("_") ? item.phase.slice(1) : `φ${item.phase}`;
      group.append(svgEl("text", { x: x + w / 2 + item.pdx * m.xScale, y: y - h - 9 - item.pdy * 18, fill: elementTextColor, "font-size": item.pfs || state.settings.fontSize, "font-family": "system-ui, sans-serif", "text-anchor": "middle", "pointer-events": "none" }, displayMath(phaseText)));
    }

    if (isSelected) {
      const outlineX = item.type === "marker" ? x - 8 : x - 4;
      const outlineW = item.type === "marker" ? 16 : w + 8;
      const outlineTop = item.type === "marker" ? Math.min(y, y - h) - 14 : isRotorElement(item) ? y - item.rotorYOffset * 58 - clamp(item.duration * .1 * 18, 7, 24) - 18 : Math.min(y, y - h) - 14;
      const outlineBottom = item.type === "marker" ? Math.max(y, y - h) + 14 : isRotorElement(item) ? y - item.rotorYOffset * 58 + clamp(item.duration * .1 * 18, 7, 24) + 18 : Math.max(y, y - h) + 14;
      group.append(svgEl("rect", { x: outlineX, y: outlineTop, width: outlineW, height: outlineBottom - outlineTop, rx: 5, fill: "none", stroke: selectedColor, "stroke-width": 1.5, "stroke-dasharray": "4 3", "pointer-events": "none" }));
      if (item.type !== "marker") {
        group.append(svgEl("rect", { x: x + w - 5, y: y - 12, width: 10, height: 24, rx: 3, fill: selectedColor, "data-handle": "duration", style: "cursor:ew-resize" }));
      }
      if (item.type === "pulse" || item.type === "marker" || isShapedElement(item)) group.append(svgEl("circle", { cx: x + w / 2, cy: y - h, r: 6, fill: selectedColor, "data-handle": "amplitude", style: "cursor:ns-resize" }));
    }
    if (!clean || group.childNodes.length) svg.append(group);
  });

  if (!clean && runtime.interaction?.snapGuide) {
    const guide = runtime.interaction.snapGuide;
    const x = m.left + guide.time * m.xScale;
    svg.append(svgEl("line", {
      x1: x, y1: m.top - 18, x2: x, y2: m.height - m.bottom,
      stroke: selectedColor, "stroke-width": 1.5, "stroke-dasharray": "5 4",
      "pointer-events": "none", "data-snap-guide": guide.label
    }));
    const labelWidth = Math.max(70, guide.label.length * 6 + 12);
    svg.append(svgEl("rect", { x: clamp(x - labelWidth / 2, m.left, m.width - m.right - labelWidth), y: m.top - 35, width: labelWidth, height: 18, rx: 5, fill: selectedColor, "pointer-events": "none" }));
    svg.append(svgEl("text", {
      x: clamp(x, m.left + labelWidth / 2, m.width - m.right - labelWidth / 2), y: m.top - 22,
      fill: "#07111e", "text-anchor": "middle", "font-size": 10, "font-family": "system-ui, sans-serif", "font-weight": 700,
      "pointer-events": "none"
    }, `${guide.label} · t=${formatNum(guide.time)}`));
  }

  if (!clean) {
    $("#emptyHint").classList.toggle("show", !state.elements.length);
    $("#timelineSummary").textContent = `${state.channels.length} channel${state.channels.length === 1 ? "" : "s"} · ${state.elements.length} element${state.elements.length === 1 ? "" : "s"} · 0–${formatNum(state.settings.timeRange)}`;
  }
  return svg;
}
