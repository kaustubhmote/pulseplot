import { STORAGE_KEY } from "./config.js";
import { $, $$, esc, formatNum } from "./utils.js";
import { state, runtime } from "./state.js";
import { snapshot, validateState } from "./model.js";
import { checkpoint, updateUndoButtons } from "./history.js";
import { renderCanvas } from "./canvas.js";
import { renderInspector } from "./inspector.js";
import { generatePython, highlightPython } from "./python.js";

export function changed({ history = false, inspector = true } = {}) {
  if (history) checkpoint();
  $("#saveStatus").textContent = "Saving…";
  clearTimeout(runtime.saveTimer);
  runtime.saveTimer = setTimeout(() => {
    try { localStorage.setItem(STORAGE_KEY, snapshot()); $("#saveStatus").textContent = "Saved locally"; }
    catch { $("#saveStatus").textContent = "Local save unavailable"; }
  }, 180);
  queueRender(inspector);
}

export function queueRender(inspector = true) {
  runtime.inspectorRenderPending = runtime.inspectorRenderPending || inspector;
  if (runtime.renderQueued) return;
  runtime.renderQueued = true;
  requestAnimationFrame(() => {
    runtime.renderQueued = false;
    const shouldRenderInspector = runtime.inspectorRenderPending;
    runtime.inspectorRenderPending = false;
    renderCanvas();
    renderChannels();
    renderSettings();
    if (shouldRenderInspector) renderInspector();
    renderCode();
    updateUndoButtons();
  });
}

export function renderAll() { renderCanvas(); renderChannels(); renderSettings(); renderInspector(); renderCode(); updateUndoButtons(); }

export function renderChannels() {
  const list = $("#channelList");
  if (list.contains(document.activeElement)) return;
  list.innerHTML = state.channels.map((channel, index) => `
    <div class="channel-item" data-channel-id="${esc(channel.id)}">
      <input aria-label="Channel ${index + 1} name" data-channel-name value="${esc(channel.name)}">
      <span class="channel-position" aria-label="Channel ${index + 1} y position" title="Automatic pulseplot y position">y=${esc(formatNum(channel.value))}</span>
      <button class="btn tiny danger" data-remove-channel title="Remove channel" ${state.channels.length === 1 ? "disabled" : ""}>×</button>
    </div>`).join("");
}

export function renderSettings() {
  $$('[data-setting]').forEach(input => {
    const key = input.dataset.setting;
    if (document.activeElement === input) return;
    if (input.type === "checkbox") input.checked = Boolean(state.settings[key]);
    else input.value = state.settings[key];
  });
  document.documentElement.dataset.theme = state.settings.theme;
}

export function renderCode() {
  const code = generatePython();
  $("#codeOutput").innerHTML = highlightPython(code);
  const problems = validateState();
  const message = $("#validationMessage");
  message.className = `validation${problems.length ? " warning" : ""}`;
  message.textContent = problems.length ? problems.join(" · ") : "Sequence is valid.";
}
