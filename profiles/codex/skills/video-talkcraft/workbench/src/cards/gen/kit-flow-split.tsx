import React from "react";
import type { CardDef } from "../types";
import { Stage, useBeat, commonFields, bounded, fit, text, ink, muted, KIT_CATEGORY } from "../explain-kit";

const Flow: React.FC<Record<string, unknown>> = (p) => {
  const beat = useBeat(p.pace);
  const weights = [0, 1, 2].map((i) => bounded(p[`value${i}`], 0, 0, 1000000));
  const total = weights.reduce((a, b) => a + b, 0);
  const colors = [text(p.accent), "#536FC4", "#BE5265"];
  let offset = 0;
  return <Stage title={p.title} note={p.note} transparent={p.transparent}>
    <svg width="864" height="355" viewBox="0 0 864 355" style={{ position: "absolute", top: 108, left: 48 }}>
      <text x="12" y="124" fontSize={fit(p.source, 24, 165)} fill={ink}>{text(p.source)}</text>
      <text x="12" y="162" fontSize="30" fontWeight="700" fill={ink}>{total}</text>
      {weights.map((value, i) => {
        const h = total ? value / total * 90 : 0;
        const sy = 130 + offset;
        offset += h;
        const dy = 20 + i * 115;
        const q = beat(0.45 + i * 0.5, 1.1);
        return <g key={i}>
          <path d={`M 190 ${sy} C 375 ${sy}, 405 ${dy}, 585 ${dy} L 585 ${dy + h} C 405 ${dy + h}, 375 ${sy + h}, 190 ${sy + h} Z`} fill={colors[i]} opacity={0.3 + 0.55 * q} style={{ clipPath: `inset(0 ${(1 - q) * 100}% 0 0)` }} />
          <rect x="585" y={dy} width="8" height={h} fill={colors[i]} opacity={q} />
          <text x="616" y={dy + 23} fontSize={fit(p[`label${i}`], 22, 238)} fill={ink} opacity={q}>{text(p[`label${i}`])}</text>
          <text x="616" y={dy + 51} fontSize="19" fill={muted} opacity={q}>{value} · {total ? (value / total * 100).toFixed(1) : "0"}%</text>
        </g>;
      })}
      {!total && <text x="240" y="188" fill={muted} fontSize="22">总量为 0，暂无流量分配</text>}
    </svg>
  </Stage>;
};

export const card: CardDef = {
  id: "kit-flow-split", name: "流向分配图", category: KIT_CATEGORY, durationInFrames: 240, component: Flow,
  schema: [
    { type: "text", key: "title", label: "标题", default: "这批请求，最终流向哪里？" },
    { type: "text", key: "source", label: "来源名称", default: "全部请求" },
    { type: "text", key: "note", label: "来源 / 单位", default: "演示数据 · 带宽按数值占比绘制 · 总量自动求和" },
    ...["自动解决", "人工处理", "等待补充"].flatMap((label, i) => [
      { type: "text" as const, key: `label${i}`, label: `去向${i + 1}`, default: label },
      { type: "number" as const, key: `value${i}`, label: `数量${i + 1}`, default: [60, 25, 15][i], min: 0, max: 1000000 },
    ]), ...commonFields,
  ],
};
