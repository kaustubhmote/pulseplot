import { SHAPE_SPECS } from "./config.js";
import { clamp, formatNum } from "./utils.js";

export function parseShape(shape) {
  const [rawName, ...rawParams] = String(shape || "gauss").split("_");
  const name = SHAPE_SPECS[rawName] ? rawName : "gauss";
  const spec = SHAPE_SPECS[name];
  const params = spec.params.map((parameter, index) => {
    const value = Number(rawParams[index]);
    return Number.isFinite(value) ? value : parameter.default;
  });
  return { name, params, spec };
}

export function isShapedElement(item) { return item.type === "shaped" || item.type === "fid"; }

export function isRotorElement(item) { return item.type === "rotor"; }

export function supportsPatchStyle(item) { return item.type === "pulse" || item.type === "shaped"; }

export function composeShape(name, params = []) {
  if (name === "custom") return "custom";
  const spec = SHAPE_SPECS[name] || SHAPE_SPECS.gauss;
  if (!spec.params.length) return name;
  return `${name}_${spec.params.map((parameter, index) => formatNum(Number.isFinite(params[index]) ? params[index] : parameter.default)).join("_")}`;
}

export function shapeValues(item, samples = 36) {
  const { name, params } = parseShape(item.shape);
  if (name === "q3" || name === "q5") return gaussianCascadeValues(name);
  if (name === "reburp") return reburpValues();
  // FIDs need substantially more samples than pulse envelopes. Keep at
  // least 24 points per oscillation so higher frequencies remain smooth
  // while capping the path size to preserve interactive performance.
  const renderSamples = name === "fid" || name === "fid2"
    ? clamp(Math.ceil(Math.abs(params[0]) * 24), 96, 4096)
    : samples;
  const values = [];
  for (let i = 0; i <= renderSamples; i++) {
    const x = i / renderSamples;
    let y;
    if (name === "ramp") {
      const percent = params[0] / 100, depth = Math.abs(percent);
      y = percent >= 0 ? 1 - depth + depth * x : 1 - depth * x;
    } else if (name === "sine" || name === "grad2") y = Math.max(0, Math.sin(Math.PI * x));
    else if (name === "sinc") y = Math.abs(sinc((x - .5) * params[0]));
    else if (name === "fid" || name === "fid2") {
      y = Math.exp(-params[1] * x) * Math.cos(2 * Math.PI * params[0] * x);
      if (name === "fid2") y += Math.sin(i * 12.9898) * .05;
    } else if (name === "grad") y = Math.exp(-Math.pow(Math.abs(x - .5) / .5, params[0]));
    else if (name === "tan") {
      const percent = params[0], curvature = Math.max(.001, params[1]);
      const unit = (Math.sinh((x - .5) / curvature) - Math.sinh(-.5 / curvature)) / (Math.sinh(.5 / curvature) - Math.sinh(-.5 / curvature));
      const depth = Math.abs(percent) / 100;
      y = percent >= 0 ? 1 - depth + depth * unit : 1 - depth * unit;
    }
    else if (name === "custom") y = interpolate(item.customPoints, x);
    else y = Math.exp(-Math.pow(x - params[0], 2) / (2 * Math.pow(Math.max(.001, params[1]), 2)));
    values.push([x, y]);
  }
  if (["gauss", "fid", "fid2", "grad"].includes(name)) {
    const low = Math.min(...values.map(point => point[1]));
    const high = Math.max(...values.map(point => point[1]));
    values.forEach(point => { point[1] = (point[1] - low) / Math.max(1e-9, high - low); });
  }
  return values.map(([x, y]) => [x, clamp(y, -1.35, 1.35)]);
}

export function gaussianCascadeValues(name) {
  const components = name === "q3"
    ? [[-4.39, .306, .18 / 2], [4.57, .545, .183 / 2], [2.60, .804, .245 / 2]]
    : [[-1.48, .162, .186 / 2], [-4.34, .307, .139 / 2], [7.33, .497, .143 / 2], [-2.30, .643, .290 / 2], [13.7, .803, .137 / 2]];
  const count = 100;
  const xValues = Array.from({ length: count }, (_, index) => index / (count - 1));
  const gaussians = components.map(([, center, sigma]) => {
    const raw = xValues.map(x => Math.exp(-Math.pow(x - center, 2) / (2 * sigma ** 2)));
    const low = Math.min(...raw), high = Math.max(...raw);
    return raw.map(value => (value - low) / Math.max(1e-12, high - low));
  });
  const amplitudes = xValues.map((_, index) => Math.abs(
    components.reduce((sum, [weight], componentIndex) => sum + weight * gaussians[componentIndex][index], 0)
  ));
  const high = Math.max(...amplitudes);
  return xValues.map((x, index) => [x, amplitudes[index] / Math.max(1e-12, high)]);
}

export function reburpValues() {
  const coefficients = [.49, -1.02, 1.11, -1.57, .83, -.42, .26, -.16, .10, -.07, .04, -.03, .01, -.02, 0, -.01];
  const fullShape = Array.from({ length: 256 }, (_, index) => {
    const t = 16 * index / 255;
    return coefficients.reduce((sum, coefficient, n) => sum + coefficient * Math.cos(n * t), 0);
  });
  const high = Math.max(...fullShape);
  return fullShape.slice(0, 100).map((value, index) => [index / 99, clamp(value / Math.max(1e-12, high), -1.35, 1.35)]);
}

export function sinc(x) { return Math.abs(x) < 1e-9 ? 1 : Math.sin(Math.PI * x) / (Math.PI * x); }

export function interpolate(points, x) {
  const sorted = [...points].sort((a, b) => a[0] - b[0]);
  if (x <= sorted[0][0]) return sorted[0][1];
  for (let i = 1; i < sorted.length; i++) {
    if (x <= sorted[i][0]) {
      const [x0, y0] = sorted[i - 1], [x1, y1] = sorted[i];
      return y0 + (y1 - y0) * ((x - x0) / Math.max(.0001, x1 - x0));
    }
  }
  return sorted[sorted.length - 1][1];
}
