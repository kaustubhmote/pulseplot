export const NS = "http://www.w3.org/2000/svg";
export const STORAGE_KEY = "pulseplot-studio-v1";
export const DEFAULT_FACE_COLOR = "#ffffff";
export const DEFAULT_EDGE_COLOR = "#000000";
export const DEFAULT_TEXT_COLOR = "#000000";
export const CHANNEL_Y_SPACING = 1.5;
export const LATEX_SYMBOLS = Object.freeze({
  alpha: "α", beta: "β", gamma: "γ", delta: "δ", epsilon: "ε", varepsilon: "ϵ", zeta: "ζ", eta: "η",
  theta: "θ", vartheta: "ϑ", iota: "ι", kappa: "κ", lambda: "λ", mu: "μ", nu: "ν", xi: "ξ", omicron: "ο",
  pi: "π", varpi: "ϖ", rho: "ρ", varrho: "ϱ", sigma: "σ", varsigma: "ς", tau: "τ", upsilon: "υ",
  phi: "φ", varphi: "ϕ", chi: "χ", psi: "ψ", omega: "ω",
  Gamma: "Γ", Delta: "Δ", Theta: "Θ", Lambda: "Λ", Xi: "Ξ", Pi: "Π", Sigma: "Σ", Upsilon: "Υ",
  Phi: "Φ", Psi: "Ψ", Omega: "Ω",
  pm: "±", mp: "∓", times: "×", cdot: "·", div: "÷", ast: "∗", leq: "≤", geq: "≥", neq: "≠",
  approx: "≈", equiv: "≡", infty: "∞", partial: "∂", nabla: "∇", sum: "∑", prod: "∏", int: "∫",
  rightarrow: "→", leftarrow: "←", leftrightarrow: "↔", Rightarrow: "⇒", Leftarrow: "⇐", Leftrightarrow: "⇔",
  circ: "°", degree: "°", angstrom: "Å"
});
export const SUPERSCRIPT_CHARS = Object.freeze({ 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹", "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾", i: "ⁱ", n: "ⁿ" });
export const SUBSCRIPT_CHARS = Object.freeze({ 0: "₀", 1: "₁", 2: "₂", 3: "₃", 4: "₄", 5: "₅", 6: "₆", 7: "₇", 8: "₈", 9: "₉", "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎", a: "ₐ", e: "ₑ", h: "ₕ", i: "ᵢ", j: "ⱼ", k: "ₖ", l: "ₗ", m: "ₘ", n: "ₙ", o: "ₒ", p: "ₚ", r: "ᵣ", s: "ₛ", t: "ₜ", u: "ᵤ", v: "ᵥ", x: "ₓ" });
export const SHAPE_SPECS = {
  gauss: { label: "Gaussian", params: [{ label: "Center", default: .5, step: .05 }, { label: "Sigma", default: .1667, min: .001, step: .01 }] },
  ramp: { label: "Linear ramp", params: [{ label: "Percent", default: 40, min: -100, max: 100, step: 5 }] },
  tan: { label: "Tangential ramp", params: [{ label: "Percent", default: 50, min: -100, max: 100, step: 5 }, { label: "Curvature", default: .1, min: .001, step: .01 }] },
  fid: { label: "FID", params: [{ label: "Frequency", default: 5, step: 1 }, { label: "Decay", default: 5, min: 0, step: .5 }] },
  fid2: { label: "Noisy FID", params: [{ label: "Frequency", default: 10, step: 1 }, { label: "Decay", default: 5, min: 0, step: .5 }] },
  grad: { label: "Gradient", params: [{ label: "Rise exponent", default: 8, min: 1, step: 1 }] },
  sine: { label: "Sine", params: [] },
  grad2: { label: "Sine gradient", params: [] },
  q3: { label: "Gaussian cascade Q3", params: [] },
  q5: { label: "Gaussian cascade Q5", params: [] },
  reburp: { label: "REBURP", params: [] },
  sinc: { label: "Sinc (generated)", params: [{ label: "Lobe scale", default: 6, min: 1, step: .5 }] },
  custom: { label: "Custom envelope", params: [] }
};
export const defaults = {
  settings: {
    title: "Pulse sequence", figureWidth: 9, figureHeight: 4.5, timeRange: 20,
    snap: .25, channelSpacing: 132, fontSize: 14, grid: true, labels: true, theme: "light"
  },
  channels: [
    { id: "ch-f1", name: "f1 · ¹H", value: 1.5 },
    { id: "ch-f2", name: "f2 · ¹³C", value: 0 }
  ],
  elements: [], selectedId: null, selectedIds: [], activeChannelId: "ch-f1"
};
