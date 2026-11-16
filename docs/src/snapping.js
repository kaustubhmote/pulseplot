import { round } from "./utils.js";
import { state } from "./state.js";

export function snap(value) { return round(Math.round(value / state.settings.snap) * state.settings.snap); }

export function alignmentAnchors(item, start = item.start) {
  const duration = Math.max(0, Number(item.duration) || 0);
  if (!duration || item.type === "marker") return [{ kind: "left", time: start, offset: 0 }];
  return [
    { kind: "left", time: start, offset: 0 },
    { kind: "center", time: start + duration / 2, offset: duration / 2 },
    { kind: "right", time: start + duration, offset: duration }
  ];
}

export function snapTargets(ignoreId) {
  return state.elements
    .filter(item => item.id !== ignoreId && item.type !== "marker" && item.duration > 0)
    .flatMap(item => alignmentAnchors(item).map(anchor => ({ ...anchor, targetId: item.id })));
}

export function anchorPriority(movingKind, targetKind) {
  if (movingKind === targetKind) return 0;
  if ((movingKind === "left" && targetKind === "right") || (movingKind === "right" && targetKind === "left")) return 1;
  return 2;
}

export function magneticStart(item, rawStart, metrics, disabled = false) {
  const fallback = Math.max(0, snap(rawStart));
  if (disabled) return { value: fallback, guide: null };
  const threshold = 10;
  const moving = alignmentAnchors(item, rawStart);
  const candidates = [];
  snapTargets(item.id).forEach(target => moving.forEach(anchor => {
    const value = target.time - anchor.offset;
    if (value < -1e-8) return;
    candidates.push({
      value: Math.max(0, round(value)),
      distance: Math.abs(value - rawStart) * metrics.xScale,
      priority: anchorPriority(anchor.kind, target.kind),
      guide: { time: target.time, label: `${anchor.kind} ↔ ${target.kind}`, targetId: target.targetId }
    });
  }));
  candidates.sort((a, b) => a.distance - b.distance || a.priority - b.priority);
  return candidates[0]?.distance <= threshold ? candidates[0] : { value: fallback, guide: null };
}

export function magneticDuration(item, rawDuration, metrics, disabled = false) {
  const fallback = Math.max(state.settings.snap, snap(rawDuration));
  if (disabled) return { value: fallback, guide: null };
  const rawEnd = item.start + rawDuration;
  const candidates = snapTargets(item.id)
    .map(target => ({
      value: round(target.time - item.start),
      distance: Math.abs(target.time - rawEnd) * metrics.xScale,
      guide: { time: target.time, label: `right ↔ ${target.kind}`, targetId: target.targetId }
    }))
    .filter(candidate => candidate.value >= state.settings.snap)
    .sort((a, b) => a.distance - b.distance);
  return candidates[0]?.distance <= 10 ? candidates[0] : { value: fallback, guide: null };
}
