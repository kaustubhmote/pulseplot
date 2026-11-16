export const $ = (selector, root = document) => root.querySelector(selector);
export const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
export const deepCopy = value => JSON.parse(JSON.stringify(value));
export const uid = prefix => `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
export const round = (value, places = 4) => Number(Number(value).toFixed(places));
export const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
export const esc = value => String(value ?? "").replace(/[&<>\"]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[char]));

export function formatNum(value) {
  const number = round(value);
  return Number.isInteger(number) ? String(number) : String(number);
}
