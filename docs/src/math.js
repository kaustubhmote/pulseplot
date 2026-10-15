import { LATEX_SYMBOLS, SUPERSCRIPT_CHARS, SUBSCRIPT_CHARS } from "./config.js";

export function scriptCharacters(value, characters) {
  return [...value].map(character => characters[character] || character).join("");
}

export function displayMath(text) {
  return String(text || "")
    .replaceAll("$", "")
    .replace(/\^\{?\\(?:circ|degree)\}?/g, "°")
    .replace(/\\(?:text|mathrm|mathbf|mathit|operatorname)\{([^{}]*)\}/g, "$1")
    .replace(/\\frac\{([^{}]+)\}\{([^{}]+)\}/g, "$1⁄$2")
    .replace(/\\sqrt\{([^{}]+)\}/g, "√($1)")
    .replace(/\\([A-Za-z]+)|\\([%${}_&#])/g, (match, command, escaped) => escaped || LATEX_SYMBOLS[command] || match)
    .replace(/\\(?:,|;|:|!)/g, " ")
    .replace(/\\(?:quad|qquad)\b/g, " ")
    .replace(/\^\{([^{}]+)\}/g, (_, value) => scriptCharacters(value, SUPERSCRIPT_CHARS))
    .replace(/_\{([^{}]+)\}/g, (_, value) => scriptCharacters(value, SUBSCRIPT_CHARS))
    .replace(/\^([A-Za-z0-9+\-=()])/g, (_, value) => scriptCharacters(value, SUPERSCRIPT_CHARS))
    .replace(/_([A-Za-z0-9+\-=()])/g, (_, value) => scriptCharacters(value, SUBSCRIPT_CHARS))
    .replace(/[{}]/g, "");
}
