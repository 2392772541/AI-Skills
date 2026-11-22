#!/usr/bin/env python3
"""Check structural consistency of a storyboard snapshot; never call models or network."""
import argparse
import json
import math
import re
import sys
from pathlib import Path

class Check:
    def __init__(self, data, root):
        self.d = data
        self.root = root.resolve()
        self.errors = []
        self.warnings = []
    def issue(self, code, path, message, warning=False):
        (self.warnings if warning else self.errors).append(dict(code=code, path=path, message=message))
    def items(self, key):
        value = self.d.get(key)
        if not isinstance(value, list):
            self.issue('TYPE', key, '必须为数组。'); return []
        valid = []
        for n, item in enumerate(value):
            if not isinstance(item, dict):
                self.issue('TYPE', f'{key}[{n}]', '必须为对象。')
            else:
                valid.append(item)
        return valid
    def index(self, key, rows):
        result = {}
        for n, row in enumerate(rows):
            ident = row.get('id')
            if not isinstance(ident, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', ident):
                self.issue('ID', f'{key}[{n}].id', '需要非空的字母/数字/连字符编号。'); continue
            if ident in result:
                self.issue('DUPLICATE_ID', key, f'编号重复：{ident}')
            result[ident] = row
        return result
    def number(self, value, path, allow_zero=False):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 or (not allow_zero and value == 0):
            self.issue('DURATION', path, '需要有限的正数秒数。'); return None
        return value
    def id_list(self, value, path):
        if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
            self.issue('TYPE', path, '必须为字符串编号数组。'); return []
        if len(value) != len(set(value)):
            self.issue('DUPLICATE_REF', path, '同一数组出现重复引用。')
        return value
    def run(self):
        if not isinstance(self.d, dict):
            self.issue('TYPE', '$', '根必须为对象。'); return self.result()
        if self.d.get('schema_version') != '1.0':
            self.issue('SCHEMA_VERSION', 'schema_version', '本检查器只支持 1.0。')
        project = self.d.get('project', {})
        if not isinstance(project, dict):
            self.issue('TYPE', 'project', '必须为对象。'); project = {}
        status = project.get('status', 'draft')
        if status not in ('draft', 'ready'):
            self.issue('STATUS', 'project.status', '仅支持 draft 或 ready。')
        ready = status == 'ready'
        platform = project.get('platform', {})
        if not isinstance(platform, dict):
            self.issue('TYPE', 'project.platform', '必须为对象。'); platform = {}
        verified = platform.get('capabilities_verified') is True
        if not verified:
            self.issue('PLATFORM_UNVERIFIED', 'project.platform', '当前入口能力未核实，不能宣称平台就绪。', warning=not ready)
        max_s = platform.get('max_duration_s')
        max_refs = platform.get('max_reference_images')
        if max_s is not None and (isinstance(max_s, bool) or not isinstance(max_s, (int, float)) or not math.isfinite(max_s) or max_s <= 0):
            self.issue('CAPABILITY', 'project.platform.max_duration_s', '上限为正数或 null。'); max_s = None
        if max_refs is not None and (isinstance(max_refs, bool) or not isinstance(max_refs, int) or max_refs < 0):
            self.issue('CAPABILITY', 'project.platform.max_reference_images', '上限为非负整数或 null。'); max_refs = None
        if ready and (max_s is None or max_refs is None):
            self.issue('CAPABILITY_UNKNOWN', 'project.platform', 'ready 需要明确本任务的时长和参考图数上限。')
        names = ('source_segments', 'characters', 'props', 'scenes', 'references', 'shots', 'generation_units')
        rows = {key: self.items(key) for key in names}
        ix = {key: self.index(key, rows[key]) for key in names}
        raw = self.d.get('source_text')
        if not isinstance(raw, str) or not raw.strip():
            self.issue('SOURCE_MISSING', 'source_text', '必须保留完整原文供对账。'); raw = ''
        if not rows['source_segments']:
            self.issue('SOURCE_EMPTY', 'source_segments', '至少一个内容段。')
        for src in rows['source_segments']:
            text = src.get('text')
            if not isinstance(text, str) or not text.strip():
                self.issue('SOURCE_TEXT', src.get('id', '?'), '内容段文字不能为空。')
            elif raw and text not in raw:
                self.issue('SOURCE_QUOTE', src['id'], '内容段不是原文中的逐字片段。')
        variants = {}
        for char in rows['characters']:
            cid = char.get('id', '?')
            appearance = char.get('appearance', {})
            if not isinstance(appearance, dict):
                self.issue('TYPE', cid + '.appearance', '必须为对象。'); appearance = {}
            for field in ('age', 'gender', 'skin', 'hair', 'face', 'costume'):
                if field not in appearance:
                    self.issue('APPEARANCE', cid + '.' + field, '六要素必须显式给值或 null。')
                elif appearance[field] is not None and not isinstance(appearance[field], str):
                    self.issue('TYPE', cid + '.' + field, '取值为文字或 null。')
            vv = char.get('variants')
            if not isinstance(vv, list) or not vv:
                self.issue('VARIANT', cid, '至少登记一个基础装束版本。'); vv = []
            for variant in vv:
                if not isinstance(variant, dict) or not isinstance(variant.get('id'), str) or not variant['id']:
                    self.issue('VARIANT', cid, '每个变体需要有效 id。'); continue
                vid = variant['id']
                if vid in variants:
                    self.issue('DUPLICATE_VARIANT', cid, '重复变体编号：' + vid)
                variants[vid] = cid
            evidence = char.get('evidence', [])
            if not isinstance(evidence, list):
                self.issue('TYPE', cid + '.evidence', '必须为数组。'); evidence = []
            if not evidence:
                self.issue('EVIDENCE_MISSING', cid, '未登记原文依据或设计理由。', warning=True)
            for claim in evidence:
                if not isinstance(claim, dict):
                    self.issue('TYPE', cid + '.evidence', '每项必须为对象。'); continue
                kind = claim.get('kind')
                if kind not in ('explicit', 'inferred', 'proposed'):
                    self.issue('EVIDENCE_KIND', cid, '依据类别必须为 explicit/inferred/proposed。')
                elif kind == 'explicit':
                    quote = claim.get('quote')
                    if not isinstance(quote, str) or not quote or quote not in raw:
                        self.issue('EVIDENCE_QUOTE', cid, '标记原文明确的依据必须在原文中逐字存在。')
                elif not isinstance(claim.get('reason'), str) or not claim['reason'].strip():
                    self.issue('EVIDENCE_REASON', cid, '推导和建议需要理由。')
        for prop in rows['props']:
            owner = prop.get('initial_owner_id')
            if owner is not None and owner not in ix['characters']:
                self.issue('PROP_OWNER', prop.get('id', '?'), '初始持有角色不存在。')
        for ref in rows['references']:
            rid = ref.get('id', '?')
            if ref.get('status') not in ('planned', 'available', 'rejected'):
                self.issue('REFERENCE_STATUS', rid, '状态必须为 planned/available/rejected。')
            cid = ref.get('character_id')
            if cid is not None and cid not in ix['characters']:
                self.issue('REFERENCE_CHARACTER', rid, '参考图的角色不存在。')
            vid = ref.get('variant_id')
            if vid is not None and (vid not in variants or variants[vid] != cid):
                self.issue('REFERENCE_VARIANT', rid, '参考图变体不属于对应角色。')
            if ref.get('status') == 'available':
                path = ref.get('path')
                if not isinstance(path, str) or not path.strip():
                    self.issue('REFERENCE_FILE', rid, 'available 图片缺少真实文件路径。'); continue
                rp = Path(path)
                if not rp.is_absolute(): rp = self.root / rp
                try: rp = rp.resolve()
                except (OSError, ValueError):
                    self.issue('REFERENCE_FILE', rid, '图片路径无效。'); continue
                if not rp.is_relative_to(self.root):
                    self.issue('REFERENCE_PATH', rid, '参考图须位于工程目录内。')
                elif not rp.is_file():
                    self.issue('REFERENCE_FILE', rid, '图片文件不存在。')
        def check_state(state, location):
            if not isinstance(state, list):
                self.issue('TYPE', location, '人物状态必须为数组。'); return {}
            mapped, holders = {}, {}
            for entry in state:
                if not isinstance(entry, dict):
                    self.issue('TYPE', location, '状态项必须为对象。'); continue
                cid, vid = entry.get('character_id'), entry.get('variant_id')
                if cid not in ix['characters']:
                    self.issue('SHOT_CHARACTER', location, '引用了未登记的角色。')
                if not isinstance(cid, str):
                    continue
                if cid in mapped:
                    self.issue('DUPLICATE_CHARACTER', location, '同一角色重复出现。')
                mapped[cid] = entry
                if vid not in variants or variants[vid] != cid:
                    self.issue('SHOT_VARIANT', location, '装束版本缺失或不属于该角色。')
                for prop_id in self.id_list(entry.get('holding', []), location + '.holding'):
                    if prop_id not in ix['props']:
                        self.issue('SHOT_PROP', location, '引用了未登记的道具：' + prop_id)
                    if prop_id in holders and holders[prop_id] != cid:
                        self.issue('DOUBLE_HOLDING', location, '同一道具同时被两人独占持有：' + prop_id + '；共同搬抬需拆成明确的共同交互说明。')
                    holders[prop_id] = cid
            return mapped
        covered, total, starts, ends = set(), 0, {}, {}
        if not rows['shots']:
            self.issue('SHOTS_EMPTY', 'shots', '镜头表为空。')
        shot_order = {}
        for n, shot in enumerate(rows['shots']):
            sid = shot.get('id', '?'); shot_order[sid] = n
            if shot.get('scene_id') not in ix['scenes']:
                self.issue('SHOT_SCENE', sid, '引用了未登记的场景。')
            duration = self.number(shot.get('duration_s'), sid + '.duration_s')
            if duration is not None: total += duration
            source_ids = self.id_list(shot.get('source_ids', []), sid + '.source_ids')
            if not source_ids and not shot.get('adaptation_reason'):
                self.issue('SHOT_SOURCE', sid, '镜头需要原文段或明确的改编理由。')
            for source_id in source_ids:
                if source_id not in ix['source_segments']:
                    self.issue('SHOT_SOURCE', sid, '引用了不存在的原文段。')
                covered.add(source_id)
            if not isinstance(shot.get('purpose'), str) or not shot['purpose'].strip():
                self.issue('SHOT_PURPOSE', sid, '镜头缺少叙事或信息目的。')
            starts[sid] = check_state(shot.get('start_state', []), sid + '.start_state')
            ends[sid] = check_state(shot.get('end_state', []), sid + '.end_state')
        for src in rows['source_segments']:
            if src.get('required', True) and src.get('id') not in covered:
                self.issue('SOURCE_UNCOVERED', src.get('id', '?'), '必需原文段没有对应镜头。')
            if not src.get('required', True) and not src.get('exclusion_reason'):
                self.issue('SOURCE_EXCLUSION', src.get('id', '?'), '删减原文需记录授权依据或原因。')
        target = project.get('target_duration_s')
        if target is not None:
            target = self.number(target, 'project.target_duration_s')
            if target is not None and not math.isclose(total, target, abs_tol=0.05):
                self.issue('TOTAL_DURATION', 'shots', f'镜头总时长 {total:g}s 与目标 {target:g}s 不一致；需要修改预算或镜头表。')
        assigned = []
        for unit in rows['generation_units']:
            uid = unit.get('id', '?')
            shot_ids = self.id_list(unit.get('shot_ids', []), uid + '.shot_ids')
            if not shot_ids: self.issue('UNIT_EMPTY', uid, '生成单元至少包含一镜。')
            duration = 0
            indices = []
            for sid in shot_ids:
                if sid not in ix['shots']:
                    self.issue('UNIT_SHOT', uid, '引用不存在的镜头：' + sid); continue
                assigned.append(sid); indices.append(shot_order[sid])
                val = ix['shots'][sid].get('duration_s')
                if isinstance(val, (int, float)) and not isinstance(val, bool) and math.isfinite(val): duration += val
            if indices and indices != list(range(indices[0], indices[0] + len(indices))):
                self.issue('UNIT_ORDER', uid, '同一单元的镜头须按镜头表连续排序。')
            declared = self.number(unit.get('duration_s'), uid + '.duration_s')
            if declared is not None and not math.isclose(duration, declared, abs_tol=0.05):
                self.issue('UNIT_DURATION', uid, '单元声明时长与所含镜头之和不一致。')
            if max_s is not None and duration > max_s + 0.05:
                self.issue('UNIT_TOO_LONG', uid, '单元时长超过已登记平台上限。')
            ref_ids = self.id_list(unit.get('reference_ids', []), uid + '.reference_ids')
            if max_refs is not None and len(ref_ids) > max_refs:
                self.issue('TOO_MANY_REFERENCES', uid, '参考图数超过已登记平台上限。')
            for rid in ref_ids:
                if rid not in ix['references']:
                    self.issue('UNIT_REFERENCE', uid, '引用未登记参考资产：' + rid)
                elif ix['references'][rid].get('status') != 'available':
                    self.issue('REFERENCE_NOT_READY', uid, '引用图片尚未可用：' + rid, warning=not ready)
            if ready and platform.get('binding_verified') is not True:
                self.issue('BINDING_UNVERIFIED', uid, 'ready 需要核实当前平台绑定语法。')
            bindings = unit.get('bindings', [])
            if not isinstance(bindings, list):
                self.issue('TYPE', uid + '.bindings', '必须为数组。'); bindings = []
            tokens, bound = set(), []
            for binding in bindings:
                if not isinstance(binding, dict):
                    self.issue('TYPE', uid + '.bindings', '每项必须为对象。'); continue
                rid, token = binding.get('reference_id'), binding.get('token')
                if rid not in ref_ids:
                    self.issue('BINDING_REFERENCE', uid, '绑定引用不在本单元上传清单。')
                if not isinstance(token, str) or not token.strip():
                    self.issue('BINDING_TOKEN', uid, '绑定令牌不能为空。'); continue
                if token in tokens:
                    self.issue('DUPLICATE_BINDING', uid, '不同绑定使用了相同令牌。')
                tokens.add(token); bound.append(rid)
            if len(bound) != len(set(bound)):
                self.issue('DUPLICATE_BINDING_REF', uid, '同一参考图存在多个绑定。')
            if ready and set(bound) != set(ref_ids):
                self.issue('BINDING_INCOMPLETE', uid, '参考资产与绑定表不完整对应。')
        if len(assigned) != len(set(assigned)):
            self.issue('SHOT_ASSIGNED_TWICE', 'generation_units', '同一镜头被多个单元重复生成。')
        if set(assigned) != set(ix['shots']):
            self.issue('UNIT_COVERAGE', 'generation_units', '生成单元没有完整覆盖镜头表。')
        if assigned != [s.get('id') for s in rows['shots']]:
            self.issue('GLOBAL_UNIT_ORDER', 'generation_units', '单元合并后的镜序与完整镜头表不一致。')
        for shot in rows['shots']:
            sid = shot.get('id', '?'); prev = shot.get('continuous_from')
            if prev is None: continue
            if not isinstance(prev, str) or prev not in ix['shots'] or shot_order.get(prev, -1) >= shot_order.get(sid, -1):
                self.issue('CONTINUITY_LINK', sid, '连续性来源须为前面的有效镜头。'); continue
            for cid in set(starts.get(sid, {})) & set(ends.get(prev, {})):
                for field in ('variant_id', 'holding', 'state', 'position', 'orientation'):
                    before, after = ends[prev][cid].get(field), starts[sid][cid].get(field)
                    if field == 'holding': before, after = sorted(before or []), sorted(after or [])
                    if before != after and not shot.get('transition_reason'):
                        self.issue('CONTINUITY_MISMATCH', sid, f'{cid} 的 {field} 与 {prev} 结束状态不一致；补充真实过渡或修正。')
        return self.result(total)
    def result(self, total=0):
        return {'ok': not self.errors, 'scope': 'structural-only', 'total_duration_s': total,
                'errors': self.errors, 'warnings': self.warnings,
                'not_checked': ['原文分段是否完整忠实', '镜头叙事与物理真实性', '图像身份与画风一致性', '视频生成执行效果', '平台事实是否真实核验']}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.project.read_text(encoding='utf-8-sig'))
        report = Check(data, args.project.parent).run()
    except (OSError, ValueError, TypeError, KeyError) as exc:
        report = {'ok': False, 'scope': 'structural-only', 'errors': [{'code': 'INPUT', 'path': str(args.project), 'message': str(exc)}], 'warnings': []}
    output = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + '\n', encoding='utf-8')
    try: print(output)
    except UnicodeEncodeError: print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report['ok'] else 1

if __name__ == '__main__':
    sys.exit(main())
