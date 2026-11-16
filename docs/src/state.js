import { defaults } from "./config.js";
import { deepCopy } from "./utils.js";

export let state = deepCopy(defaults);

export function setState(project) { state = project; }

export const runtime = {
  undoStack: [], redoStack: [], interaction: null, shapeInteraction: null,
  copiedElement: null, pasteTarget: null, toastTimer: null, saveTimer: null,
  renderQueued: false, inspectorRenderPending: false
};
