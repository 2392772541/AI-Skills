import React from "react";
import type { CardDef } from "../types";
import { Stage, useBeat, commonFields, bounded, fit, text, ink, muted, KIT_CATEGORY } from "../explain-kit";

const Waterfall: React.FC<Record<string, unknown>> = (p) => {
  const beat = useBeat(p.pace);
  const start = bounded(p.start, 100, -1000000, 1000000);
  const changes = [bounded(p.a, 40, -1000000, 1000000), bounded(p.b, -25, -1000000, 1000000), bounded(p.c, 15, -1000000, 1000000)];
  const sums = [start];
  changes.forEach((n) => sums.push(sums[sums.length - 1] + n));
  const low = Math.min(0, ...sums), high = Math.max(0, ...sums);
  const range = high - low || 1;
  const y = (v: number) => 400 - (v - low) / range * 240;
  const labels = [p.startLabel, p.aLabel, p.bLabel, p.cLabel, p.endLabel];
  const values = [start, ...changes, sums[3]];
  return <Stage title={p.title} note={p.note} transparent={p.transparent}>
    <svg width="864" height="360" viewBox="0 100 864 360" style={{ position: "absolute", top: 100, left: 48, overflow: "visible" }}>
      <line x1="0" x2="864" y1={y(0)} y2={y(0)} stroke="#C7CFD4" />
      {values.map((value, i) => {
        const a = i === 0 || i === 4 ? 0 : sums[i - 1];
        const b = i === 0 || i === 4 ? value : sums[i];
        const q = beat(0.25 + i * 0.65);
        const end = a + (b - a) * q;
        const x = i * 172 + 20;
        return <g key={i} opacity={beat(i * 0.65, 0.2)}>
          {i > 0 && <line x1={x - 48} x2={x} y1={y(a)} y2={y(a)} stroke="#8B979E" strokeDasharray="4 5" opacity={i === 4 ? 0 : 1} />}
          <rect x={x} y={Math.min(y(a), y(end))} width="124" height={Math.max(2, Math.abs(y(a) - y(end)))} fill={i === 0 || i === 4 ? ink : value >= 0 ? text(p.accent) : "#C34B5B"} rx="3" />
          <text x={x + 62} y={Math.min(y(a), y(b)) - 14} textAnchor="middle" fontSize="23" fontWeight="700" fill={ink}>{i > 0 && i < 4 && value > 0 ? "+" : ""}{Math.round(value * q)}</text>
          <text x={x + 62} y="435" textAnchor="middle" fontSize={fit(labels[i], 20, 128)} fill={muted}>{text(labels[i])}</text>
        </g>;
      })}
    </svg>
  </Stage>;
};

export const card: CardDef = {
  id: "kit-waterfall", name: "增减贡献拆解", category: KIT_CATEGORY, durationInFrames: 240, component: Waterfall,
  schema: [
    { type: "text", key: "title", label: "标题", default: "结果变化，来自哪几项？" },
    { type: "text", key: "note", label: "来源 / 单位", default: "演示数据 · 单位：万元 · 终值由各项自动相加" },
    { type: "text", key: "startLabel", label: "起点名称", default: "原始收益" },
    { type: "number", key: "start", label: "起点数值", default: 100 },
    { type: "text", key: "aLabel", label: "因素一", default: "新增业务" },
    { type: "number", key: "a", label: "因素一增减", default: 40 },
    { type: "text", key: "bLabel", label: "因素二", default: "投入成本" },
    { type: "number", key: "b", label: "因素二增减", default: -25 },
    { type: "text", key: "cLabel", label: "因素三", default: "效率提升" },
    { type: "number", key: "c", label: "因素三增减", default: 15 },
    { type: "text", key: "endLabel", label: "终点名称", default: "最终收益" }, ...commonFields,
  ],
};
