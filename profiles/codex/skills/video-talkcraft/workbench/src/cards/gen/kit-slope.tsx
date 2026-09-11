import React from "react";
import type { CardDef } from "../types";
import { Stage, useBeat, commonFields, bounded, fit, text, ink, muted, KIT_CATEGORY } from "../explain-kit";

const Slope: React.FC<Record<string, unknown>> = (p) => {
  const beat = useBeat(p.pace);
  const rows = [0, 1, 2].map((i) => ({ label: text(p[`label${i}`]), from: bounded(p[`from${i}`], 0, 0, 100), to: bounded(p[`to${i}`], 0, 0, 100) }));
  const colors = [text(p.accent), "#B74661", "#536FC4"];
  const y = (n: number) => 390 - n * 2.2;
  return <Stage title={p.title} note={p.note} transparent={p.transparent}>
    <svg width="864" height="350" viewBox="0 100 864 350" style={{ position: "absolute", top: 100, left: 48 }}>
      {[0, 50, 100].map((n) => <g key={n}><line x1="165" x2="700" y1={y(n)} y2={y(n)} stroke="#DDE2E6" strokeDasharray="4 5" /><text x="430" y={y(n) - 8} textAnchor="middle" fill={muted} fontSize="13">{n}%</text></g>)}
      <text x="190" y="125" textAnchor="middle" fill={ink} fontSize="22">{text(p.before)}</text>
      <text x="670" y="125" textAnchor="middle" fill={ink} fontSize="22">{text(p.after)}</text>
      {rows.map((row, i) => {
        const q = beat(0.6 + i * 0.6, 1);
        return <g key={i} opacity={beat(i * 0.3, 0.3)}>
          <line x1="190" y1={y(row.from)} x2={190 + q * 480} y2={y(row.from + (row.to - row.from) * q)} stroke={colors[i]} strokeWidth="4" />
          <circle cx="190" cy={y(row.from)} r="6" fill={colors[i]} />
          <circle cx={190 + q * 480} cy={y(row.from + (row.to - row.from) * q)} r="7" fill={colors[i]} />
        </g>;
      })}
    </svg>
    <div style={{ position: "absolute", left: 65, right: 65, top: 435, display: "flex", gap: 24 }}>
      {rows.map((row, i) => <div key={i} style={{ flex: 1, minWidth: 0, color: colors[i], fontSize: fit(row.label, 17, 210), overflowWrap: "anywhere" }}>{row.label}<div style={{ fontSize: 16, marginTop: 5, opacity: beat(2.4 + i * 0.4) }}>{row.from}% → {row.to}% · {row.to - row.from > 0 ? "+" : ""}{Math.round((row.to - row.from) * 10) / 10} pp</div></div>)}
    </div>
  </Stage>;
};

export const card: CardDef = {
  id: "kit-slope", name: "前后指标迁移", category: KIT_CATEGORY, durationInFrames: 240, component: Slope,
  schema: [
    { type: "text", key: "title", label: "标题", default: "同一批指标，前后发生了什么？" },
    { type: "text", key: "before", label: "起始阶段", default: "调整前" },
    { type: "text", key: "after", label: "结束阶段", default: "调整后" },
    { type: "text", key: "note", label: "来源说明", default: "演示数据 · pp 表示百分点 · 不代表因果结论" },
    ...["任务完成率", "返工占比", "自动处理率"].flatMap((label, i) => [
      { type: "text" as const, key: `label${i}`, label: `指标${i + 1}`, default: label },
      { type: "slider" as const, key: `from${i}`, label: `指标${i + 1}原值`, default: [50, 75, 15][i], min: 0, max: 100, step: 1 },
      { type: "slider" as const, key: `to${i}`, label: `指标${i + 1}现值`, default: [90, 25, 60][i], min: 0, max: 100, step: 1 },
    ]), ...commonFields,
  ],
};
