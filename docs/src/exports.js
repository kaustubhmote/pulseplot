import { state } from "./state.js";
import { renderCanvas } from "./canvas.js";
import { toast } from "./notifications.js";

export function download(name, blob) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url; anchor.download = name; anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function cleanSvgString() {
  const svg = renderCanvas({ clean: true });
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  return `<?xml version="1.0" encoding="UTF-8"?>\n${new XMLSerializer().serializeToString(svg)}`;
}

export async function exportPng() {
  const svgText = cleanSvgString();
  const blob = new Blob([svgText], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  try {
    const image = new Image();
    await new Promise((resolve, reject) => { image.onload = resolve; image.onerror = reject; image.src = url; });
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(state.settings.figureWidth * 300);
    canvas.height = Math.round(state.settings.figureHeight * 300);
    const context = canvas.getContext("2d");
    context.fillStyle = "#ffffff"; context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(image, 0, 0, canvas.width, canvas.height);
    const png = await new Promise(resolve => canvas.toBlob(resolve, "image/png", 1));
    download("pulse_sequence.png", png);
    toast("High-resolution PNG exported");
  } catch {
    toast("PNG export failed in this browser");
  } finally { URL.revokeObjectURL(url); }
}
