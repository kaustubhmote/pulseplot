import { $ } from "./utils.js";
import { runtime } from "./state.js";

export function toast(message) {
  const node = $("#toast");
  node.textContent = message; node.classList.add("show");
  clearTimeout(runtime.toastTimer); runtime.toastTimer = setTimeout(() => node.classList.remove("show"), 2400);
}
