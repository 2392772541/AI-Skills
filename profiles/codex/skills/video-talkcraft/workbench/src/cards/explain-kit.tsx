import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import type { PropField } from "./types";
import { FONT_STACK, power2Out, tw } from "./shared";

export const KIT_CATEGORY = "讲解增强";
export const ink = "#202428";
export const muted = "#657078";
export const text = (value: unknown) => String(value ?? "");
export const num = (value: unknown, fallback: number) => Number.isFinite(Number(value)) ? Number(value) : fallback;
export const bounded = (value: unknown, fallback: number, min: number, max: number) => Math.max(min, Math.min(max, num(value, fallback)));
export const lines = (value: unknown, max = 5) => text(value).split("\n").map((s) => s.trim()).filter(Boolean).slice(0, max);
export const fit = (value: unknown, max = 30, width = 400) => Math.max(12, Math.min(max, width / Math.max(1, Array.from(text(value)).length)));

export const useBeat = (speed: unknown) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps * bounded(speed, 1, 0.7, 1.8);
  return (start: number, duration = 0.6) => tw(t, start, duration, power2Out);
};

export const commonFields: PropField[] = [
  { type: "color", key: "accent", label: "强调色", default: "#147D73" },
  { type: "slider", key: "pace", label: "动画节奏", default: 1, min: 0.7, max: 1.8, step: 0.1 },
  { type: "boolean", key: "transparent", label: "透明底（叠加素材）", default: false },
];

export const titleField = (value: string): PropField => ({ type: "text", key: "title", label: "标题", default: value });
export const stringField = (key: string, label: string, value: string): PropField => ({ type: "text", key, label, default: value });
export const valueFields = (names: string[], values: number[], max = 1000000): PropField[] => names.flatMap((name, i) => [
  stringField(`label${i}`, `项目${i + 1}`, name),
  { type: "number", key: `value${i}`, label: `数值${i + 1}`, default: values[i], min: 0, max } as PropField,
]);
export const palette = (accent: unknown) => [text(accent), "#536FC4", "#BD5369", "#AD751B"];
export const SvgLabel: React.FC<{ x: number; y: number; value: unknown; width?: number; size?: number; color?: string; anchor?: "start" | "middle" | "end" }> = ({ x, y, value, width = 200, size = 22, color = ink, anchor = "middle" }) =>
  <text x={x} y={y} textAnchor={anchor} fill={color} fontSize={fit(value, size, width)}>{text(value)}</text>;
export const Plot: React.FC<{ children: React.ReactNode }> = ({ children }) => <svg viewBox="0 0 864 360" width="864" height="360" style={{ position: "absolute", left: 48, top: 112 }}>{children}</svg>;

export const Stage: React.FC<{ title: unknown; note?: unknown; transparent?: unknown; children: React.ReactNode }> = ({ title, note, transparent, children }) => {
  const { width, height } = useVideoConfig();
  const scale = Math.min(width / 960, height / 540);
  return <AbsoluteFill style={{ background: transparent ? "transparent" : "#F5F7F8", color: ink, fontFamily: FONT_STACK, overflow: "hidden" }}>
    <div style={{ position: "absolute", width: 960, height: 540, left: (width - 960 * scale) / 2, top: (height - 540 * scale) / 2, transform: `scale(${scale})`, transformOrigin: "0 0" }}>
      <div style={{ position: "absolute", top: 32, left: 48, right: 48, fontWeight: 750, fontSize: fit(title, 32, 850), overflowWrap: "anywhere", lineHeight: 1.2 }}>{text(title)}</div>
      {children}
      <div style={{ position: "absolute", bottom: 23, left: 48, right: 48, color: muted, fontSize: fit(note, 16, 840), overflowWrap: "anywhere" }}>{text(note)}</div>
    </div>
  </AbsoluteFill>;
};
