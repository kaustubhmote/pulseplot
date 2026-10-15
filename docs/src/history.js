import { STORAGE_KEY, defaults } from "./config.js";
import { $, deepCopy } from "./utils.js";
import { state, setState, runtime } from "./state.js";
import { normalizeState, snapshot } from "./model.js";
import { renderAll } from "./render.js";

export function loadStored() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) setState(normalizeState(JSON.parse(stored)));
  } catch (error) {
    console.warn("Could not restore saved project", error);
    setState(deepCopy(defaults));
  }
  document.documentElement.dataset.theme = state.settings.theme || "light";
}

export function checkpoint() {
  const current = snapshot();
  if (runtime.undoStack[runtime.undoStack.length - 1] !== current) runtime.undoStack.push(current);
  if (runtime.undoStack.length > 80) runtime.undoStack.shift();
  runtime.redoStack = [];
  updateUndoButtons();
}

export function restore(serialized) {
  setState(normalizeState(JSON.parse(serialized)));
  document.documentElement.dataset.theme = state.settings.theme;
  renderAll();
}

export function undo() {
  if (!runtime.undoStack.length) return;
  runtime.redoStack.push(snapshot());
  restore(runtime.undoStack.pop());
  updateUndoButtons();
}

export function redo() {
  if (!runtime.redoStack.length) return;
  runtime.undoStack.push(snapshot());
  restore(runtime.redoStack.pop());
  updateUndoButtons();
}

export function updateUndoButtons() {
  $("#undoBtn").disabled = !runtime.undoStack.length;
  $("#redoBtn").disabled = !runtime.redoStack.length;
}
