import React from "react";
import type { CardDef } from "../types";
import { Stage, useBeat, commonFields, fit, text, ink, KIT_CATEGORY } from "../explain-kit";

const Continuity: React.FC<Record<string, unknown>> = (p) => {
  const beat = useBeat(p.pace);
  const expand = beat(1.2, 1.1);
  const regroup = p.regroup ? beat(4.1, 1) : 0;
  const spread = expand * (1 - regroup);
  const colors = [text(p.accent), "#536FC4", "#BD5369"];
  return <Stage title={p.title} note={p.note} transparent={p.transparent}>
    <div style={{ position: "absolute", top: 113, left: 80, right: 80, textAlign: "center", color: ink, fontSize: fit(p.subject, 25, 740), opacity: 1 - spread * 0.7 }}>{text(p.subject)}</div>
    {[0, 1, 2].map((i) => {
      const x = 364 + (i - 1) * 272 * spread;
      const y = 198 + i * 22 * (1 - spread);
      return <div key={i} style={{ position: "absolute", left: x, top: y, width: 232, height: 154, transform: `scale(${0.92 + 0.08 * expand}) translateY(${(1 - beat(i * 0.13)) * 22}px)`, opacity: beat(i * 0.13), zIndex: 3 - i }}>
        <div style={{ height: "100%", background: colors[i], color: "white", border: "2px solid #FFFFFF", borderRadius: 6, padding: 22, boxSizing: "border-box" }}>
          <div style={{ fontSize: 17, opacity: 0.75 }}>0{i + 1}</div>
          <div style={{ marginTop: 18, fontWeight: 700, fontSize: fit(p[`label${i}`], 25, 185), overflowWrap: "anywhere" }}>{text(p[`label${i}`])}</div>
        </div>
        <div style={{ marginTop: 20, fontSize: fit(text(p[`detail${i}`]).slice(0, 36), 18, 400), lineHeight: 1.5, textAlign: "center", overflowWrap: "anywhere", opacity: spread * beat(2.4 + i * 0.2) }}>{text(p[`detail${i}`]).slice(0, 36)}</div>
      </div>;
    })}
    <div style={{ position: "absolute", top: 438, left: 80, right: 80, textAlign: "center", fontSize: fit(p.conclusion, 26, 740), fontWeight: 700, opacity: p.regroup ? regroup : beat(4.1) }}>{text(p.conclusion)}</div>
  </Stage>;
};
export const card: CardDef = {
  id: "kit-object-continuity", name: "结构拆解重组", category: KIT_CATEGORY, durationInFrames: 270, component: Continuity,
  schema: [
    { type: "text", key: "title", label: "标题", default: "把一个系统，拆成三个部分" },
    { type: "text", key: "subject", label: "整体名称", default: "视频制作工作流" },
    ...["内容", "画面", "节奏"].flatMap((label, i) => [
      { type: "text" as const, key: `label${i}`, label: `部件${i + 1}名称`, default: label },
      { type: "textarea" as const, key: `detail${i}`, label: `部件${i + 1}说明（最多36字）`, default: ["先明确这一段要讲清什么", "为每个信息选择合适画面", "让动画跟随讲解的停顿"][i] },
    ]),
    { type: "text", key: "conclusion", label: "收束结论", default: "三个部分，回到同一个目标" },
    { type: "boolean", key: "regroup", label: "结尾重新合拢", default: true },
    { type: "text", key: "note", label: "补充说明", default: "示意结构 · 按你的产品、机制或流程替换" }, ...commonFields,
  ],
};
