import React from "react";
import type { CardDef } from "./types";
import { Stage, Plot, SvgLabel as L, useBeat, commonFields, titleField, stringField, text, bounded, palette, ink, muted, KIT_CATEGORY } from "./explain-kit";

type Props = Record<string, unknown>;
const node = (x: number, y: number, label: unknown, color: string, width = 180) => <g><rect x={x - width / 2} y={y - 24} width={width} height="48" rx="5" fill={color} /><L x={x} y={y + 7} value={label} width={width - 24} color="white" size={21} /></g>;

const Decision: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), active = p.choice === "right" ? 1 : 0, colors = palette(p.accent);
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    <g opacity={beat(0)}><path d="M 432 0 L 562 65 L 432 130 L 302 65 Z" fill={ink} /><L x={432} y={72} value={p.question} width={200} color="white" /></g>
    {[0, 1].map((i) => <g key={i} opacity={beat(0.7 + i * 0.3) * (i === active ? 1 : 0.35)}>
      <path d={`M 432 130 V 160 H ${216 + i * 432} V 215`} stroke={colors[i]} strokeWidth="4" fill="none" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - beat(0.6, 1)} />
      <L x={216 + i * 432} y={150} value={p[`branch${i}`]} color={colors[i]} />
      {node(216 + i * 432, 240, p[`result${i}`], colors[i], 275)}
    </g>)}
    <g opacity={beat(2.5)}><L x={432} y={338} value={p.conclusion} width={760} size={24} /></g>
  </Plot></Stage>;
};

const Feedback: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), colors = palette(p.accent);
  const points = [[170, 70], [690, 70], [690, 270], [170, 270]];
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    <path d="M 280 70 H 580 M 690 100 V 240 M 580 270 H 280 M 170 240 V 100" stroke="#C1CAD0" strokeWidth="3" fill="none" />
    {points.map(([x, y], i) => <g key={i} opacity={beat(i * 0.55)}>{node(x, y, p[`label${i}`], colors[i], 220)}</g>)}
    <path d="M 280 70 H 580 V 270 H 280 Z" pathLength="1" stroke={text(p.accent)} strokeWidth="5" strokeDasharray="0.025 0.975" strokeDashoffset={-beat(0.8, 3.6)} fill="none" />
    <g opacity={beat(2.2)}><L x={432} y={177} value={p.center} width={300} size={27} /></g>
    <L x={432} y={342} value="顺时针反馈路径" size={15} color={muted} />
  </Plot></Stage>;
};

const Layers: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), colors = palette(p.accent), q = beat(0.7, 1.8);
  const focus = bounded(p.focus, 1, 1, 4) - 1;
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    {[3, 2, 1, 0].map((i) => {
      const y = 70 + i * (14 + q * 50);
      return <g key={i} opacity={beat(0.1) * (i === focus ? 1 : 0.65)}>
        <path d={`M 30 ${y + 22} L 310 ${y - 18} L 460 ${y + 20} L 180 ${y + 60} Z`} fill={colors[i]} stroke="white" strokeWidth="2" />
        <line x1="450" y1={y + 20} x2="530" y2={y + 20} stroke={colors[i]} opacity={q} />
        <g opacity={q}><L x={552} y={y + 26} value={p[`label${i}`]} anchor="start" width={290} color={colors[i]} /></g>
      </g>;
    })}
  </Plot></Stage>;
};

const Hierarchy: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), colors = palette(p.accent);
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    <g opacity={beat(0)}>{node(432, 35, p.root, ink, 240)}</g>
    {[0, 1, 2].map((i) => {
      const x = 144 + i * 288;
      return <g key={i} opacity={beat(0.6 + i * 0.25)}>
        <path d={`M 432 59 V 96 H ${x} V 146`} fill="none" stroke={colors[i]} strokeWidth="3" />
        {node(x, 170, p[`label${i}`], colors[i], 230)}
        <path d={`M ${x} 194 V 265`} stroke={colors[i]} strokeWidth="3" />
        <g opacity={beat(1.8 + i * 0.3)}><L x={x} y={303} value={p[`child${i}`]} width={245} size={21} color={colors[i]} /></g>
      </g>;
    })}
  </Plot></Stage>;
};

const Evidence: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), colors = palette(p.accent);
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    <L x={220} y={25} value={p.left} width={340} size={24} /><L x={640} y={25} value={p.right} width={340} size={24} />
    {[0, 1, 2].map((i) => <g key={i} opacity={beat(0.3 + i * 0.7)}>
      <line x1="15" x2="849" y1={68 + i * 91} y2={68 + i * 91} stroke="#CCD3D8" />
      <L x={220} y={110 + i * 91} value={p[`claim${i}`]} width={365} size={23} />
      <L x={433} y={110 + i * 91} value="→" width={40} color={colors[i]} />
      <L x={640} y={110 + i * 91} value={p[`evidence${i}`]} width={360} size={23} color={colors[i]} />
    </g>)}
  </Plot></Stage>;
};

const create = (id: string, name: string, component: React.FC<Props>, schema: CardDef["schema"]): CardDef => ({ id, name, component, category: KIT_CATEGORY, durationInFrames: 270, schema: [titleField(name), ...schema, stringField("note", "来源 / 说明", "示意内容 · 请按实际材料填写"), ...commonFields] });
export const decision = create("kit-decision", "条件分支决策", Decision, [
  stringField("question", "判断条件", "信息是否充分？"), stringField("branch0", "左分支", "是"), stringField("branch1", "右分支", "否"),
  stringField("result0", "左侧动作", "开始制作"), stringField("result1", "右侧动作", "补充资料"), stringField("conclusion", "收束文字", "先判断条件，再选择动作"),
  { type: "select", key: "choice", label: "突出分支", default: "left", options: [{ value: "left", label: "左侧" }, { value: "right", label: "右侧" }] },
]);
export const feedback = create("kit-feedback", "四步反馈闭环", Feedback, [
  ...["观察", "判断", "行动", "复盘"].map((s, i) => stringField(`label${i}`, `环节${i + 1}`, s)), stringField("center", "中心主题", "持续修正"),
]);
export const layers = create("kit-layers", "分层剖面展开", Layers, [
  ...["表现层", "交互层", "逻辑层", "数据层"].map((s, i) => stringField(`label${i}`, `层级${i + 1}`, s)),
  { type: "slider", key: "focus", label: "突出第几层", default: 1, min: 1, max: 4, step: 1 },
]);
export const hierarchy = create("kit-hierarchy", "层级结构展开", Hierarchy, [
  stringField("root", "根节点", "视频制作"), ...["策划", "制作", "验收"].flatMap((s, i) => [stringField(`label${i}`, `分支${i + 1}`, s), stringField(`child${i}`, `分支${i + 1}细项`, ["选题与脚本", "配音与画面", "审片与修改"][i])]),
]);
export const evidence = create("kit-evidence", "观点证据对照", Evidence, [
  stringField("left", "左列标题", "需要说明的观点"), stringField("right", "右列标题", "对应证据 / 待核实项"),
  ...["速度更快", "错误更少", "使用更方便"].flatMap((s, i) => [stringField(`claim${i}`, `观点${i + 1}`, s), stringField(`evidence${i}`, `证据${i + 1}`, ["填写计时记录", "填写评测结果", "填写用户测试记录"][i])]),
]);
