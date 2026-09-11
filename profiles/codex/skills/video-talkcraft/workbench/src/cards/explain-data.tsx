import React from "react";
import type { CardDef, PropField } from "./types";
import { Stage, Plot, SvgLabel as L, useBeat, commonFields, titleField, stringField, valueFields, bounded, text, palette, ink, muted, KIT_CATEGORY } from "./explain-kit";

type Props = Record<string, unknown>;
const valuesOf = (p: Props, count = 4) => Array.from({ length: count }, (_, i) => bounded(p[`value${i}`], 0, 0, 1000000));
const numberField = (key: string, label: string, value: number, max = 100): PropField => ({ type: "number", key, label, default: value, min: 0, max });

const Funnel: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), values = valuesOf(p), max = Math.max(1, ...values), colors = palette(p.accent);
  const valid = values.every((n, i) => !i || n <= values[i - 1]);
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    {values.map((value, i) => {
      const width = value / max * 480 * beat(i * 0.55);
      return <g key={i} opacity={beat(i * 0.55)}>
        <rect x={295 - width / 2} y={10 + i * 77} width={width} height="60" rx="3" fill={colors[i]} />
        <L x={570} y={35 + i * 77} value={p[`label${i}`]} width={265} anchor="start" />
        <L x={570} y={60 + i * 77} value={`${value}${i && values[i - 1] ? ` · 留存 ${(value / values[i - 1] * 100).toFixed(1)}%` : ""}`} anchor="start" width={275} size={17} color={muted} />
      </g>;
    })}
    {!valid && <L x={432} y={347} value="数值存在上升，请确认是否为同一批次漏斗" width={750} size={16} color="#B74661" />}
  </Plot></Stage>;
};

const Heatmap: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), accent = text(p.accent);
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    {[0, 1, 2].map((i) => <g key={i}><L x={284 + i * 185} y={30} value={p[`col${i}`]} width={168} size={21} /><L x={150} y={103 + i * 84} value={p[`row${i}`]} anchor="end" width={142} size={20} /></g>)}
    {Array.from({ length: 9 }, (_, i) => {
      const value = bounded(p[`cell${i}`], 0, 0, 100), q = beat(i * 0.18);
      return <g key={i} opacity={q}><rect x={197 + i % 3 * 185} y={54 + Math.floor(i / 3) * 84} width="174" height="74" rx="3" fill={accent} opacity={0.08 + value / 100 * 0.92} /><L x={284 + i % 3 * 185} y={100 + Math.floor(i / 3) * 84} value={value} width={100} color={value > 50 ? "white" : ink} /></g>;
    })}
    <L x={475} y={346} value="0 = 低强度 · 100 = 高强度" width={400} size={16} color={muted} />
  </Plot></Stage>;
};

const Gantt: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), colors = palette(p.accent);
  const total = bounded(p.days, 14, 1, 365);
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    {[0, 1, 2, 3, 4].map((i) => <g key={i}><line x1={220 + i * 150} x2={220 + i * 150} y1="35" y2="330" stroke="#D2D9DE" /><L x={220 + i * 150} y={22} value={`${(total * i / 4).toFixed(1)}天`} width={110} size={16} color={muted} /></g>)}
    {[0, 1, 2, 3].map((i) => {
      const start = bounded(p[`start${i}`], 0, 0, total), end = bounded(p[`end${i}`], total, 0, total);
      const valid = end >= start, q = beat(i * 0.5);
      return <g key={i}><L x={190} y={84 + i * 69} value={p[`label${i}`]} anchor="end" width={178} size={21} /><rect x={220 + start / total * 600} y={56 + i * 69} width={Math.max(0, end - start) / total * 600 * q} height="40" rx="3" fill={colors[i]} />{!valid && <L x={490} y={84 + i * 69} value="结束早于开始，请调整" color="#B74661" size={17} />}</g>;
    })}
  </Plot></Stage>;
};

const Interval: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), colors = palette(p.accent);
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    {[0, 25, 50, 75, 100].map((n) => <g key={n}><line x1={220 + n * 6} x2={220 + n * 6} y1="20" y2="300" stroke="#DDE2E6" /><L x={220 + n * 6} y={333} value={n} size={16} color={muted} /></g>)}
    {[0, 1, 2].map((i) => {
      const a = bounded(p[`low${i}`], 0, 0, 100), b = bounded(p[`high${i}`], 100, 0, 100), point = bounded(p[`point${i}`], 50, 0, 100);
      const valid = a <= point && point <= b, y = 65 + i * 97, q = beat(i * 0.65);
      return <g key={i} opacity={q}><L x={190} y={y + 7} value={p[`label${i}`]} anchor="end" width={175} />
        {valid ? <><line x1={220 + a * 6} x2={220 + (a + (b - a) * q) * 6} y1={y} y2={y} stroke={colors[i]} strokeWidth="8" /><line x1={220 + a * 6} x2={220 + a * 6} y1={y - 14} y2={y + 14} stroke={colors[i]} strokeWidth="3" /><line x1={220 + b * 6} x2={220 + b * 6} y1={y - 14} y2={y + 14} stroke={colors[i]} strokeWidth="3" /><circle cx={220 + point * 6} cy={y} r="9" fill={ink} /><L x={520} y={y + 33} value={`${a} – ${b} · 点估计 ${point}`} width={450} size={16} color={muted} /></> : <L x={520} y={y} value="需要：下界 ≤ 点估计 ≤ 上界" width={550} color="#B74661" size={17} />}
      </g>;
    })}
  </Plot></Stage>;
};

const Histogram: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), values = valuesOf(p), max = Math.max(1, ...values), colors = palette(p.accent);
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    <line x1="50" x2="814" y1="285" y2="285" stroke={muted} />
    {values.map((v, i) => {
      const h = v / max * 215 * beat(i * 0.4);
      return <g key={i}><rect x={60 + i * 187} y={285 - h} width="184" height={h} fill={colors[i]} /><L x={152 + i * 187} y={270 - h} value={v} width={170} /><L x={152 + i * 187} y={322} value={p[`label${i}`]} width={175} size={19} /></g>;
    })}
  </Plot></Stage>;
};

const Pareto: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), values = valuesOf(p), total = values.reduce((a, b) => a + b, 0), max = Math.max(1, ...values);
  const rows = values.map((value, id) => ({ value, id })).sort((a, b) => b.value - a.value || a.id - b.id);
  let sum = 0;
  const points = rows.map((r, i) => { sum += r.value; return [130 + i * 190, 275 - (total ? sum / total : 0) * 220]; });
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    <line x1="45" x2="814" y1="275" y2="275" stroke={muted} />
    {rows.map((r, i) => { const h = r.value / max * 190 * beat(i * 0.45); return <g key={r.id}><rect x={65 + i * 190} y={275 - h} width="130" height={h} fill={text(p.accent)} opacity="0.75" /><L x={130 + i * 190} y={302} value={p[`label${r.id}`]} width={175} size={18} /><L x={130 + i * 190} y={329} value={r.value} size={17} /></g>; })}
    <polyline points={points.map((p) => p.join(",")).join(" ")} fill="none" stroke="#BD5369" strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - beat(1.8, 1.3)} />
    {points.map(([x, y], i) => <g key={i} opacity={beat(1.8 + i * 0.3)}><circle cx={x} cy={y} r="6" fill="#BD5369" /><L x={x} y={y - 15} value={`${(total ? (275 - y) / 220 * 100 : 0).toFixed(0)}%`} size={18} color="#BD5369" /></g>)}
  </Plot></Stage>;
};

const Bullet: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), colors = palette(p.accent);
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    {[0, 1, 2].map((i) => {
      const v = bounded(p[`value${i}`], 0, 0, 100), target = bounded(p[`target${i}`], 80, 0, 100), y = 25 + i * 107;
      return <g key={i}><L x={190} y={y + 29} value={p[`label${i}`]} anchor="end" width={180} />
        {[0, 1, 2].map((j) => <rect key={j} x={230 + j * 170} y={y} width="170" height="48" fill={["#E4E9EC", "#D2DAE0", "#BCC8CF"][j]} />)}
        <rect x="230" y={y + 14} width={v * 5.1 * beat(i * 0.6)} height="20" fill={colors[i]} />
        <line x1={230 + target * 5.1} x2={230 + target * 5.1} y1={y - 7} y2={y + 55} stroke={ink} strokeWidth="3" />
        <L x={485} y={y + 81} value={`实际 ${v} / 目标 ${target}`} width={430} size={17} color={muted} />
      </g>;
    })}
  </Plot></Stage>;
};

const Donut: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), values = valuesOf(p), total = values.reduce((a, b) => a + b, 0), colors = palette(p.accent);
  let offset = 0;
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    <circle cx="245" cy="170" r="120" fill="none" stroke="#E0E6E9" strokeWidth="46" />
    {values.map((v, i) => {
      const share = total ? v / total : 0, begin = offset; offset += share;
      return <g key={i}><circle cx="245" cy="170" r="120" fill="none" stroke={colors[i]} strokeWidth="46" pathLength="1" strokeDasharray={`${share * beat(i * 0.45)} 1`} strokeDashoffset={-begin} transform="rotate(-90 245 170)" /><g opacity={beat(i * 0.45)}><rect x="475" y={35 + i * 76} width="12" height="35" fill={colors[i]} /><L x={510} y={56 + i * 76} value={p[`label${i}`]} width={320} anchor="start" /><L x={510} y={81 + i * 76} value={`${v} · ${(share * 100).toFixed(1)}%`} width={300} anchor="start" size={17} color={muted} /></g></g>;
    })}
    <L x={245} y={164} value={total} width={170} size={38} /><L x={245} y={198} value={total ? "总量" : "暂无数据"} size={18} color={muted} />
  </Plot></Stage>;
};

const Rank: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), from = valuesOf(p), to = [0, 1, 2, 3].map((i) => bounded(p[`to${i}`], 0, 0, 1000000));
  const max = Math.max(1, ...from, ...to), q = beat(1.2, 1.8), values = from.map((n, i) => n + (to[i] - n) * q), colors = palette(p.accent);
  const order0 = from.map((v, id) => ({ v, id })).sort((a, b) => b.v - a.v || a.id - b.id).map((r) => r.id);
  const order1 = to.map((v, id) => ({ v, id })).sort((a, b) => b.v - a.v || a.id - b.id).map((r) => r.id);
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    {values.map((v, i) => {
      const y = 30 + (order0.indexOf(i) + (order1.indexOf(i) - order0.indexOf(i)) * q) * 78;
      const labelOpacity = q > 0 && q < 1 ? Math.abs(q - 0.5) * 2 : 1;
      return <g key={i} opacity={beat(i * 0.1)}><g opacity={labelOpacity}><L x={182} y={y + 28} value={p[`label${i}`]} anchor="end" width={170} size={20} /><L x={728} y={y + 28} value={Math.round(v)} width={120} size={22} color={colors[i]} /></g><rect x="205" y={y} width={v / max * 490} height="43" fill={colors[i]} rx="3" opacity="0.85" /></g>;
    })}
    <L x={450} y={354} value={q < 1 ? "从起点值迁移至终点值" : "终点排名"} width={480} size={16} color={muted} />
  </Plot></Stage>;
};

const Venn: React.FC<Props> = (p) => {
  const beat = useBeat(p.pace), q = beat(0.6, 1.4), accent = text(p.accent);
  return <Stage title={p.title} note={p.note} transparent={p.transparent}><Plot>
    <circle cx={225 + q * 95} cy="170" r="145" fill={accent} opacity="0.2" stroke={accent} strokeWidth="3" />
    <circle cx={639 - q * 95} cy="170" r="145" fill="#BD5369" opacity="0.2" stroke="#BD5369" strokeWidth="3" />
    <L x={275} y={176} value={p.a} width={145} color={accent} size={24} /><L x={590} y={176} value={p.b} width={145} color="#BD5369" size={24} />
    <g opacity={beat(2.1)}><L x={432} y={176} value={p.overlap} width={94} size={22} /><L x={432} y={350} value={p.conclusion} width={770} size={23} /></g>
  </Plot></Stage>;
};

const create = (id: string, name: string, component: React.FC<Props>, schema: PropField[], note = "演示数据 · 请替换为有来源的实际数值"): CardDef => ({ id, name, component, category: KIT_CATEGORY, durationInFrames: 270, schema: [titleField(name), ...schema, stringField("note", "来源 / 单位", note), ...commonFields] });
export const funnel = create("kit-funnel", "逐级转化漏斗", Funnel, valueFields(["访问", "试用", "激活", "留存"], [1000, 600, 320, 180]));
export const heatmap = create("kit-heatmap", "矩阵强度揭示", Heatmap, [
  ...["方案 A", "方案 B", "方案 C"].map((s, i) => stringField(`row${i}`, `行${i + 1}`, s)),
  ...["效率", "质量", "易用"].map((s, i) => stringField(`col${i}`, `列${i + 1}`, s)),
  ...[85, 40, 60, 55, 90, 35, 25, 65, 95].map((v, i) => numberField(`cell${i}`, `第${Math.floor(i / 3) + 1}行第${i % 3 + 1}列`, v)),
]);
export const gantt = create("kit-gantt", "并行任务排期", Gantt, [numberField("days", "总天数", 14, 365), ...["策划", "素材", "制作", "验收"].flatMap((s, i) => [stringField(`label${i}`, `任务${i + 1}`, s), numberField(`start${i}`, `任务${i + 1}开始日`, [0, 2, 4, 11][i], 365), numberField(`end${i}`, `任务${i + 1}结束日`, [4, 7, 12, 14][i], 365)])]);
export const interval = create("kit-interval", "估计区间揭示", Interval, [
  ...["试验 A", "试验 B", "试验 C"].flatMap((s, i) => [stringField(`label${i}`, `对象${i + 1}`, s), numberField(`low${i}`, `下界${i + 1}`, [15, 35, 55][i]), numberField(`point${i}`, `点估计${i + 1}`, [30, 60, 75][i]), numberField(`high${i}`, `上界${i + 1}`, [45, 80, 95][i])]),
], "演示区间 · 请说明区间定义；不自动计算置信度");
export const histogram = create("kit-histogram", "频数分布展开", Histogram, valueFields(["0–10", "10–20", "20–30", "30–40"], [12, 38, 26, 9]), "演示频数 · 仅适用于四个连续等宽分组");
export const pareto = create("kit-pareto", "累计贡献聚焦", Pareto, valueFields(["问题 A", "问题 B", "问题 C", "其他"], [50, 25, 15, 10]), "演示数据 · 自动降序 · 红线为累计占比");
export const bullet = create("kit-bullet", "目标达成对照", Bullet, [
  ...valueFields(["进度", "覆盖", "完成"], [65, 85, 40], 100), ...[80, 90, 75].map((v, i) => numberField(`target${i}`, `目标${i + 1}`, v)),
], "演示数据 · 统一 0–100 刻度 · 黑线表示目标");
export const donut = create("kit-donut", "构成占比环图", Donut, valueFields(["内容", "制作", "推广", "其他"], [40, 30, 20, 10]));
export const rank = create("kit-rank", "排名位置重排", Rank, [...valueFields(["项目 A", "项目 B", "项目 C", "项目 D"], [80, 60, 40, 20]), ...[35, 95, 70, 45].map((v, i) => numberField(`to${i}`, `项目${i + 1}终点值`, v, 1000000))], "演示数据 · 两个状态之间的插值，不代表实际历史轨迹");
export const venn = create("kit-venn", "集合交集聚焦", Venn, [stringField("a", "集合 A", "用户需求"), stringField("b", "集合 B", "产品能力"), stringField("overlap", "交集", "价值"), stringField("conclusion", "结论", "找到两者共同覆盖的部分")], "集合关系示意 · 圆面积不表示数量");
