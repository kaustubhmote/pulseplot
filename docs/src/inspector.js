import { SHAPE_SPECS } from "./config.js";
import { $, clamp, esc } from "./utils.js";
import { state } from "./state.js";
import { selected, selectedItems, overlaps } from "./model.js";
import { parseShape, isShapedElement, isRotorElement, supportsPatchStyle, composeShape } from "./shapes.js";
import { changed } from "./render.js";
import { svgEl } from "./svg.js";
import { snap } from "./snapping.js";
import { toast } from "./notifications.js";

export function shapeControlsHtml(item) {
  const { name, params, spec } = parseShape(item.shape);
  const options = Object.entries(SHAPE_SPECS).map(([value, shape]) =>
    `<option value="${value}" ${value === name ? "selected" : ""}>${esc(shape.label)}</option>`
  ).join("");
  const parameterFields = spec.params.map((parameter, index) => `
    <div class="field"><label>${esc(parameter.label)}</label><input data-shape-param="${index}" type="number" value="${params[index]}" step="${parameter.step ?? .1}" ${parameter.min !== undefined ? `min="${parameter.min}"` : ""} ${parameter.max !== undefined ? `max="${parameter.max}"` : ""}></div>
  `).join("");
  return `
    <div class="field wide-2"><label title="Shape family (sp)">Shape (sp)</label><select data-shape-name>${options}</select></div>
    ${parameterFields}
    ${spec.params.length ? `<div class="field wide-2"><label title="Generated pulseplot shape">Generated sp</label><input data-shape-preview value="${esc(composeShape(name, params))}" readonly></div>` : ""}`;
}

export function sharedProperty(items, key) {
  const value = items[0]?.[key];
  return items.every(item => Object.is(item[key], value)) ? value : undefined;
}

export function batchFieldHtml(items, key, label, { type = "text", min = null, max = null, step = null, placeholder = "Mixed" } = {}) {
  const value = sharedProperty(items, key);
  const mixed = value === undefined;
  const attributes = [
    `data-batch-prop="${key}"`,
    mixed ? 'data-mixed="true"' : "",
    type !== "text" ? `type="${type}"` : "",
    min !== null ? `min="${min}"` : "",
    max !== null ? `max="${max}"` : "",
    step !== null ? `step="${step}"` : "",
    `value="${mixed ? "" : esc(value)}"`,
    `placeholder="${esc(placeholder)}"`
  ].filter(Boolean).join(" ");
  return `<div class="field"><label>${label}</label><input ${attributes}></div>`;
}

export function batchSelectHtml(items, key, label, options) {
  const value = sharedProperty(items, key);
  const mixed = value === undefined;
  return `<div class="field"><label>${label}</label><select data-batch-prop="${key}" ${mixed ? 'data-mixed="true"' : ""}>
    ${mixed ? '<option value="" selected>Mixed</option>' : ""}
    ${options.map(option => `<option value="${esc(option.value)}" ${String(value) === String(option.value) ? "selected" : ""}>${esc(option.label)}</option>`).join("")}
  </select></div>`;
}

export function renderBatchInspector(root, items) {
  const fields = [batchSelectHtml(items, "channel", "Channel", state.channels.map(channel => ({ value: channel.id, label: channel.name }))), batchFieldHtml(items, "start", "Start · st", { type: "number", min: 0, step: state.settings.snap })];
  if (items.every(item => item.type !== "marker")) fields.push(batchFieldHtml(items, "duration", "Duration · p/d", { type: "number", min: state.settings.snap, step: state.settings.snap }));
  if (items.every(item => item.type === "pulse" || item.type === "marker" || isShapedElement(item))) fields.push(batchFieldHtml(items, "amplitude", "Power · pl", { type: "number", min: -1.5, max: 1.5, step: .05 }));
  if (items.every(item => !isRotorElement(item))) {
    fields.push(batchFieldHtml(items, "phase", "Phase · ph"));
    if (items.every(item => isShapedElement(item))) fields.push(batchFieldHtml(items, "shape", "Shape · sp"));
    if (items.every(item => item.type !== "delay")) {
      fields.push(batchFieldHtml(items, "facecolor", "Facecolor · fc", { placeholder: "Mixed color" }));
      fields.push(batchFieldHtml(items, "edgecolor", "Edgecolor · ec", { placeholder: "Mixed color" }));
    }
    if (items.every(item => item.type === "pulse" || item.type === "marker" || isShapedElement(item))) fields.push(batchFieldHtml(items, "textcolor", "Text color", { placeholder: "Mixed color" }));
    if (items.every(supportsPatchStyle)) {
      fields.push(batchFieldHtml(items, "hatch", "Hatch · h"));
      fields.push(batchFieldHtml(items, "alpha", "Alpha · al", { type: "number", min: 0, max: 1, step: .05 }));
    }
    fields.push(batchFieldHtml(items, "text", "Annotation · tx"));
    fields.push(batchFieldHtml(items, "tdx", "Text x", { type: "number", step: .1 }));
    fields.push(batchFieldHtml(items, "tdy", "Text y", { type: "number", step: .1 }));
    fields.push(batchFieldHtml(items, "tfs", "Text size", { type: "number", min: 6, max: 40, step: 1 }));
    fields.push(batchFieldHtml(items, "pdx", "Phase x", { type: "number", step: .1 }));
    fields.push(batchFieldHtml(items, "pdy", "Phase y", { type: "number", step: .1 }));
    fields.push(batchFieldHtml(items, "pfs", "Phase size", { type: "number", min: 6, max: 40, step: 1 }));
    fields.push(batchSelectHtml(items, "allowOverlap", "Overlap", [{ value: true, label: "Allowed" }, { value: false, label: "Prevented" }]));
  }
  root.innerHTML = `
    <div class="inspector-head">
      <span class="type-badge">${items.length} selected</span><h2>Batch inspector</h2>
      <div class="inspector-actions"><button class="btn tiny" data-inspector-action="duplicate">Duplicate all</button><button class="btn tiny danger" data-inspector-action="delete">Delete all</button></div>
    </div>
    <div class="inspector-grid">${fields.join("")}</div>`;
}

export function applyBatchControl(control) {
  const items = selectedItems();
  const key = control.dataset.batchProp;
  let value = control.type === "number" ? Number(control.value) : control.value;
  if (key === "allowOverlap") value = value === "true";
  if (key === "alpha") value = clamp(Number.isFinite(value) ? value : 1, 0, 1);
  const previous = items.map(item => item[key]);
  items.forEach(item => { item[key] = value; });
  if (items.some(item => overlaps(item))) {
    items.forEach((item, index) => { item[key] = previous[index]; });
    control.value = sharedProperty(items, key) ?? "";
    toast("Batch change rejected because it would create an overlap");
    return false;
  }
  if (key === "channel") state.activeChannelId = value;
  changed({ inspector: false });
  return true;
}

export function renderInspector() {
  const root = $("#inspector");
  const selection = selectedItems();
  if (!selection.length) {
    root.innerHTML = '<div class="inspector-empty">Select an element to edit duration, amplitude, phase, text, and shape.</div>';
    return;
  }
  if (selection.length > 1) {
    renderBatchInspector(root, selection);
    return;
  }
  const item = selection[0];
  if (isRotorElement(item)) {
    root.innerHTML = `
      <div class="inspector-head">
        <span class="type-badge">rotor</span><h2>Rotor inspector</h2>
        <div class="inspector-actions"><button class="btn tiny" data-inspector-action="duplicate">Duplicate</button><button class="btn tiny danger" data-inspector-action="delete">Delete</button></div>
      </div>
      <div class="inspector-grid">
        <div class="field wide-2"><label>Channel</label><select data-prop="channel">${state.channels.map(channel => `<option value="${esc(channel.id)}" ${channel.id === item.channel ? "selected" : ""}>${esc(channel.name)}</option>`).join("")}</select></div>
        <div class="field"><label title="Left edge of rotor overlay">Start</label><input data-prop="start" type="number" min="0" step="${state.settings.snap}" value="${item.start}"></div>
        <div class="field"><label title="Rotor body length">Length</label><input data-prop="duration" type="number" min="${state.settings.snap}" step="${state.settings.snap}" value="${item.duration}"></div>
        <div class="field"><label title="Size of the Matplotlib inset axes in inches">Inset size</label><input data-prop="rotorInsetWidth" type="number" min="0.25" step="0.25" value="${item.rotorInsetWidth}"></div>
        <div class="field"><label title="Vertical offset above the assigned channel">Y offset</label><input data-prop="rotorYOffset" type="number" step="0.05" value="${item.rotorYOffset}"></div>
      </div>`;
    return;
  }
  const isPulse = item.type === "pulse" || item.type === "marker" || isShapedElement(item);
  const hasPatchStyle = supportsPatchStyle(item);
  root.innerHTML = `
    <div class="inspector-head">
      <span class="type-badge">${esc(item.type)}</span><h2>Element inspector</h2>
      <div class="inspector-actions"><button class="btn tiny" data-inspector-action="duplicate">Duplicate</button><button class="btn tiny danger" data-inspector-action="delete">Delete</button></div>
    </div>
    <div class="inspector-grid">
      <div class="field wide-2"><label>Channel</label><select data-prop="channel">${state.channels.map(channel => `<option value="${esc(channel.id)}" ${channel.id === item.channel ? "selected" : ""}>${esc(channel.name)}</option>`).join("")}</select></div>
      <div class="field"><label title="Start time (st)">Start · st</label><input data-prop="start" type="number" min="0" step="${state.settings.snap}" value="${item.start}"></div>
      ${item.type !== "marker" ? `<div class="field"><label title="${item.type === "delay" ? "Delay length (d)" : "Duration (p)"}">${item.type === "delay" ? "Length · d" : "Duration · p"}</label><input data-prop="duration" type="number" min="${state.settings.snap}" step="${state.settings.snap}" value="${item.duration}"></div>` : `<div class="field"><label>Duration</label><input value="0" disabled></div>`}
      ${isPulse ? `<div class="field"><label title="Power / amplitude (pl)">Power · pl</label><input data-prop="amplitude" type="number" min="-1.5" max="1.5" step="0.05" value="${item.amplitude}"></div>` : `<div class="field"><label>Power · pl</label><input value="—" disabled></div>`}
      <div class="field"><label title="Phase (ph)">Phase · ph</label><input data-prop="phase" value="${esc(item.phase)}" placeholder="1 / rec"></div>
      ${item.type !== "delay" ? `<div class="field"><label title="Face color (fc)">Facecolor · fc</label><input data-prop="facecolor" type="color" value="${esc(item.facecolor)}"></div>` : `<div class="field"><label>Facecolor · fc</label><input value="—" disabled></div>`}
      ${item.type !== "delay" ? `<div class="field"><label title="Edge color (ec)">Edgecolor · ec</label><input data-prop="edgecolor" type="color" value="${esc(item.edgecolor)}"></div>` : `<div class="field"><label>Edgecolor · ec</label><input value="—" disabled></div>`}
      ${isPulse ? `<div class="field"><label title="Annotation and phase text color">Text color</label><input data-prop="textcolor" type="color" value="${esc(item.textcolor)}"></div>` : `<div class="field"><label>Text color</label><input value="—" disabled></div>`}
      ${hasPatchStyle ? `<div class="field"><label title="Matplotlib hatch pattern (h)">Hatch · h</label><input data-prop="hatch" value="${esc(item.hatch)}" placeholder="///, xx, .."></div>` : ""}
      ${hasPatchStyle ? `<div class="field"><label title="Patch opacity (al)">Alpha · al</label><input data-prop="alpha" type="number" min="0" max="1" step="0.05" value="${item.alpha}"></div>` : ""}
      <div class="field wide-4"><label title="Annotation (tx); LaTeX accepted">Annotation · tx</label><input data-prop="text" value="${esc(item.text)}" placeholder="$\\tau$, $90^\\circ$, CP"></div>
      <div class="field"><label title="Text x offset (tdx)">Text x</label><input data-prop="tdx" type="number" step="0.1" value="${item.tdx}"></div>
      <div class="field"><label title="Text y offset (tdy)">Text y</label><input data-prop="tdy" type="number" step="0.1" value="${item.tdy}"></div>
      <div class="field"><label title="Text size (tfs)">Text size</label><input data-prop="tfs" type="number" min="6" max="40" value="${item.tfs}"></div>
      <div class="field"><label title="Phase x offset (pdx)">Phase x</label><input data-prop="pdx" type="number" step="0.1" value="${item.pdx}"></div>
      <div class="field"><label title="Phase y offset (pdy)">Phase y</label><input data-prop="pdy" type="number" step="0.1" value="${item.pdy}"></div>
      <div class="field"><label title="Phase size (pfs)">Phase size</label><input data-prop="pfs" type="number" min="6" max="40" value="${item.pfs}"></div>
      ${isShapedElement(item) ? shapeControlsHtml(item) : ""}
      ${isShapedElement(item) ? `<label class="check-field field wide-3"><input data-prop="truncateOff" type="checkbox" ${item.truncateOff || ["fid", "fid2"].includes(parseShape(item.shape).name) ? "checked" : ""} ${["fid", "fid2"].includes(parseShape(item.shape).name) ? "disabled" : ""}> Truncate edges (troff)${["fid", "fid2"].includes(parseShape(item.shape).name) ? " · automatic" : ""}</label>` : ""}
      <label class="check-field field wide-3"><input data-prop="allowOverlap" type="checkbox" ${item.allowOverlap ? "checked" : ""}> Allow overlap</label>
      ${isShapedElement(item) && parseShape(item.shape).name === "custom" ? `<div class="field wide-6 custom-shape"><label>Custom envelope · drag points</label><svg id="shapeEditor" viewBox="0 0 480 100" aria-label="Custom shape curve editor"></svg></div>` : ""}
    </div>`;
  if (isShapedElement(item) && parseShape(item.shape).name === "custom") renderShapeEditor(item);
}

export function renderShapeEditor(item) {
  const svg = $("#shapeEditor");
  if (!svg) return;
  const pad = 9, width = 480, height = 100;
  svg.replaceChildren();
  svg.append(svgEl("line", { x1: pad, y1: height - pad, x2: width - pad, y2: height - pad, stroke: "var(--border)", "stroke-width": 1 }));
  const points = item.customPoints.map(([x, y]) => [pad + x * (width - pad * 2), height - pad - y * (height - pad * 2)]);
  svg.append(svgEl("polyline", { points: points.map(p => p.join(",")).join(" "), fill: "none", stroke: "var(--accent)", "stroke-width": 2 }));
  points.forEach(([x, y], index) => svg.append(svgEl("circle", { cx: x, cy: y, r: 6, fill: "var(--accent-2)", stroke: "var(--panel)", "stroke-width": 2, "data-point-index": index, style: "cursor:move" })));
}
