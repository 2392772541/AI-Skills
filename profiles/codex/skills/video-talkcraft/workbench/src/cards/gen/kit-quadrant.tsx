import React from "react";
import type { CardDef } from "../types";
import { Stage, useBeat, commonFields, bounded, fit, text, ink, muted, KIT_CATEGORY } from "../explain-kit";

const Quadrant: React.FC<Record<string, unknown>> = (p) => {
  const beat = useBeat(p.pace);
  const x0 = bounded(p.x0, 25, 0, 100), y0 = bounded(p.y0, 30, 0, 100);
  const x1 = bounded(p.x1, 75, 0, 100), y1 = bounded(p.y1, 80, 0, 100);
  const q = beat(1.3, 1.8);
  const px = (n: number) => 100 + n * 4.8;
  const py = (n: number) => 330 - n * 2.5;
  const accent = text(p.accent);
  return <Stage title={p.title} note={p.note} transparent={p.transparent}>
    <svg width="660" height="390" viewBox="0 0 660 390" style={{ position: "absolute", top: 100, left: 20 }}>
      <g opacity={beat(0, 0.5)}>
        <rect x="100" y="80" width="240" height="125" fill={accent} opacity="0.07" />
        <rect x="340" y="205" width="240" height="125" fill="#B74661" opacity="0.07" />
        <path d="M 100 65 V 330 H 600" stroke={muted} fill="none" strokeWidth="2" />
        <path d="M 340 80 V 330 M 100 205 H 580" stroke="#BCC5CB" fill="none" strokeDasharray="5 6" />
        <text x="90" y="352" fill={muted} fontSize="14">0</text><text x="565" y="352" fill={muted} fontSize="14">100</text>
        <text x="62" y="87" fill={muted} fontSize="14">100</text>
        <text x="340" y="378" textAnchor="middle" fill={ink} fontSize={fit(p.xLabel, 19, 350)}>{text(p.xLabel)}</text>
        <text x="95" y="36" fill={ink} fontSize={fit(p.yLabel, 19, 400)}>{text(p.yLabel)}</text>
      </g>
      <g opacity={beat(0.6)}>
        <circle cx={px(x0)} cy={py(y0)} r="9" fill="none" stroke={accent} strokeWidth="2" />
        <line x1={px(x0)} y1={py(y0)} x2={px(x0 + (x1 - x0) * q)} y2={py(y0 + (y1 - y0) * q)} stroke={accent} strokeWidth="3" strokeDasharray="5 5" />
        <circle cx={px(x0 + (x1 - x0) * q)} cy={py(y0 + (y1 - y0) * q)} r="12" fill={accent} />
      </g>
    </svg>
    <div style={{ position: "absolute", left: 690, top: 145, width: 215 }}>
      <div style={{ color: accent, fontWeight: 750, fontSize: fit(p.subject, 28, 210), overflowWrap: "anywhere" }}>{text(p.subject)}</div>
      <div style={{ marginTop: 30, fontSize: 17, color: muted }}>起点 ({x0}, {y0})</div>
      <div style={{ marginTop: 12, fontSize: 21, opacity: beat(2.5) }}>终点 ({x1}, {y1})</div>
      <div style={{ marginTop: 32, lineHeight: 1.5, fontSize: 22, overflowWrap: "anywhere", opacity: beat(3) }}>{text(p.conclusion).slice(0, 60)}</div>
    </div>
  </Stage>;
};
export const card: CardDef = {
  id: "kit-quadrant", name: "双轴位置迁移", category: KIT_CATEGORY, durationInFrames: 240, component: Quadrant,
  schema: [
    { type: "text", key: "title", label: "标题", default: "用两个维度，解释一次变化" },
    { type: "text", key: "xLabel", label: "横轴（0–100）", default: "自动化程度" },
    { type: "text", key: "yLabel", label: "纵轴（0–100）", default: "交付质量" },
    { type: "text", key: "subject", label: "对象名称", default: "方案 A" },
    ...["x0", "y0", "x1", "y1"].map((key, i) => ({ type: "slider" as const, key, label: ["起点 X", "起点 Y", "终点 X", "终点 Y"][i], default: [25, 30, 75, 80][i], min: 0, max: 100, step: 1 })),
    { type: "textarea", key: "conclusion", label: "结论（最多60字）", default: "两个维度同时改善" },
    { type: "text", key: "note", label: "来源说明", default: "演示坐标 · 维度与评价依据需按实际内容填写" }, ...commonFields,
  ],
};
