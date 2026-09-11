"""Read-only skill discovery, persistent user labels, and restart-safe change history."""
from __future__ import annotations
import copy
import hashlib
import json
import os
import threading
import time
from pathlib import Path
from datetime import datetime, timezone
import sys

ROOT = Path(os.environ.get('AI_SKILLS_HOME', r'D:\AI-Skills'))
sys.path.insert(0, str(ROOT / 'scripts'))
from skilllib import parse_frontmatter, infer_categories
from guidebook import GUIDES, CATEGORIES

SKIP = {'.system', '.git', '.codex', 'node_modules', '__pycache__', 'archived', 'archive',
        'incoming', 'needs-review', '.venv', 'venv', 'plugins', 'cache', 'vendor', '.pytest_cache'}

def now():
    return datetime.now().astimezone().isoformat(timespec='seconds')

def excluded(path):
    return any(p.lower() in SKIP or 'backup' in p.lower() or p.startswith('.') for p in path.parts)

def canonical(path):
    return str(path.resolve()).casefold()

def read_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8-sig'))

def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, path)

class Catalog:
    def __init__(self, roots=None, state_dir=None, interval=15):
        self.roots = [Path(p) for p in (roots or [ROOT / 'skills', Path.home() / '.codex' / 'skills'])]
        self.state_dir = Path(state_dir or ROOT / 'registry' / 'personal-console')
        self.state_path = self.state_dir / 'observations.json'
        self.labels_path = self.state_dir / 'labels.json'
        self.lock = threading.RLock()
        self.interval = interval
        self.stop = threading.Event()
        self.error = ''
        self.scanned_at = None
        self.duration = 0
        self.thread = None
        self.state = read_json(self.state_path, {'items': {}, 'events': [], 'initialized': False})
        self.labels = read_json(self.labels_path, {})
        self.guide_revisions = read_json(Path(__file__).parent / 'guide-revisions.json', {})

    def discover(self):
        found = {}
        seen_dirs = set()
        ignored = []
        try:
            installations = read_json(Path.home() / '.agents' / '.skill-lock.json', {}).get('skills', {})
        except (OSError, ValueError):
            installations = {}
        def walk(directory, root):
            # Reject cache/system destinations even if linked into an allowed root.
            real = directory.resolve()
            if any(p.lower() in {'.system', 'plugins', 'cache', 'openai-bundled', 'openai-curated-remote'} for p in real.parts):
                ignored.append(str(directory)); return
            key = canonical(directory)
            skill_md = directory / 'SKILL.md'
            if skill_md.is_file():
                sid = hashlib.sha256(key.encode()).hexdigest()[:16]
                if sid in found:
                    found[sid]['aliases'].append(str(directory)); return
                data = skill_md.read_bytes()
                if len(data) > 2_000_000:
                    raise ValueError('SKILL.md 过大：' + str(skill_md))
                fm, issues = parse_frontmatter(data.decode('utf-8-sig', errors='replace'))
                files, digest, latest = [], hashlib.sha256(), 0
                def onerror(exc):
                    raise exc
                for base, dirs, names in os.walk(real, followlinks=False, onerror=onerror):
                    dirs[:] = sorted(d for d in dirs if not excluded(Path(d)) and not Path(base, d).is_symlink() and not getattr(Path(base, d), 'is_junction', lambda: False)())
                    for name in sorted(names):
                        p = Path(base, name)
                        if name.startswith('.') or p.is_symlink(): continue
                        stat = p.stat()
                        rel = p.relative_to(real).as_posix()
                        files.append(rel)
                        digest.update(f'{rel}:{stat.st_size}:{stat.st_mtime_ns}'.encode())
                        latest = max(latest, stat.st_mtime)
                digest.update(data)
                name = str(fm.get('name') or directory.name)
                description = str(fm.get('description') or '尚未填写技能描述')
                found[sid] = {'id': sid, 'name': name, 'description': description,
                    'path': str(real), 'aliases': [str(directory)], 'root': str(root),
                    'fingerprint': digest.hexdigest(), 'md_hash': hashlib.sha256(data).hexdigest(),
                    'files': files, 'file_count': len(files), 'modified_at': datetime.fromtimestamp(latest, timezone.utc).astimezone().isoformat(timespec='seconds'),
                    'categories': infer_categories(name, description), 'issues': issues, 'status': 'active'}
                receipt = installations.get(directory.name, {})
                if receipt.get('source') and canonical(Path.home() / '.agents' / 'skills' / directory.name) == key:
                    found[sid]['source_hint'] = 'external'
                    found[sid]['source_evidence'] = '本机 .agents/.skill-lock.json 安装记录匹配此目录；不代表当前内容与上游完全一致'
                return
            if key in seen_dirs: return
            seen_dirs.add(key)
            for child in sorted(directory.iterdir()):
                if child.is_dir():
                    if excluded(Path(child.name)):
                        ignored.append(str(child)); continue
                    walk(child, root)
        for root in self.roots:
            if not root.is_dir():
                raise OSError('监控目录不可用，保留上次结果：' + str(root))
            # Root .codex is allowed; exclusion applies to descendants only.
            for child in sorted(root.iterdir()):
                if child.is_dir():
                    if excluded(Path(child.name)):
                        ignored.append(str(child)); continue
                    walk(child, root)
        return found, ignored

    def scan(self):
        with self.lock:
            started = time.monotonic()
            try:
                found, ignored = self.discover()
                old = self.state['items']
                events = list(self.state['events'])
                stamp = now()
                def event(kind, row):
                    events.append({'at': stamp, 'kind': kind, 'id': row['id'], 'name': row['name'], 'path': row['path']})
                for sid, row in found.items():
                    prev = old.get(sid)
                    row['first_seen'] = prev['first_seen'] if prev else stamp
                    if self.state['initialized']:
                        if not prev: event('added', row)
                        elif prev['status'] == 'missing': event('restored', row)
                        elif prev['fingerprint'] != row['fingerprint']: event('modified', row)
                for sid, prev in old.items():
                    if sid not in found:
                        row = dict(prev, status='missing')
                        found[sid] = row
                        if prev['status'] != 'missing': event('removed', row)
                state = {'items': found, 'events': events[-1000:], 'initialized': True, 'ignored': ignored}
                if state != self.state: atomic(self.state_path, state)
                self.state = state
                self.scanned_at = stamp
                self.error = ''
            except (OSError, ValueError) as exc:
                self.error = str(exc)
            self.duration = round(time.monotonic() - started, 3)
            return not self.error

    def start(self):
        self.scan()
        def watch():
            while not self.stop.wait(self.interval): self.scan()
        self.thread = threading.Thread(target=watch, daemon=True, name='personal-skill-watcher')
        self.thread.start()

    def snapshot(self):
        with self.lock:
            items = []
            for sid, row in self.state['items'].items():
                item = dict(row)
                item.update(self.labels.get(sid, {}))
                item.setdefault('source', row.get('source_hint', 'unknown'))
                if sid in self.labels:
                    item['source_evidence'] = '用户在管理台确认的来源标记'
                item.setdefault('favorite', False)
                item.setdefault('note', '')
                guide = copy.deepcopy(GUIDES.get(row['name'], {}))
                reviewed_hashes = self.guide_revisions.get(row['name'], [])
                guide_status = 'reviewed' if guide and row['md_hash'] in reviewed_hashes else 'stale' if guide else 'pending'
                if not guide:
                    guide = {'title':row['name'],'summary':'这是刚发现或尚未整理说明的技能，具体用途需要先核对下面的原始说明。','when':'先确认技能的实际用途，再决定是否使用。','needs':'以原始技能说明为准。','output':'尚未核对，暂不承诺具体结果。','example':'先帮我读懂这个技能是做什么的。','boundary':'暂无核对过的大白话说明，可在右侧补充。','categories':['other']}
                custom = item.get('guide_override', {})
                if custom:
                    guide.update(custom)
                    guide_status = 'manual'
                item['guide'] = guide
                item['guide_status'] = guide_status
                item['categories'] = self.labels.get(sid, {}).get('categories', guide['categories'])
                items.append(item)
            counts = {}
            for row in items:
                if row['status'] == 'active': counts[row['name']] = counts.get(row['name'], 0) + 1
            for row in items: row['copies'] = counts.get(row['name'], 0)
            return copy.deepcopy({'items': items, 'categories': CATEGORIES, 'events': list(reversed(self.state['events'])),
                'monitor': {'scanned_at': self.scanned_at, 'interval': self.interval, 'error': self.error,
                    'running': bool(self.thread and self.thread.is_alive()), 'duration': self.duration,
                    'roots': [str(p) for p in self.roots], 'ignored': self.state.get('ignored', [])}})

    def annotate(self, sid, payload):
        with self.lock:
            if sid not in self.state['items']: raise KeyError(sid)
            prior = self.labels.get(sid, {})
            source = payload.get('source', prior.get('source', self.state['items'][sid].get('source_hint', 'unknown')))
            if source not in {'unknown', 'self', 'external', 'builtin'}: raise ValueError('来源类型无效')
            note = payload.get('note', prior.get('note', ''))
            if not isinstance(note, str) or len(note) > 2000: raise ValueError('备注最多 2000 字')
            favorite = payload.get('favorite', prior.get('favorite', False))
            if not isinstance(favorite, bool): raise ValueError('收藏字段无效')
            labels = copy.deepcopy(self.labels)
            updated = dict(prior, source=source, note=note, favorite=favorite)
            if 'categories' in payload:
                cats = payload['categories']
                if not isinstance(cats, list) or not 1 <= len(cats) <= 8 or any(not isinstance(c, str) or not c.strip() or len(c) > 40 or any(ord(v)<32 for v in c) for c in cats):
                    raise ValueError('请填写 1–8 个分类，每个最多 40 字')
                updated['categories'] = list(dict.fromkeys(c.strip() for c in cats))
            if 'guide_override' in payload:
                guide = payload['guide_override']
                allowed = {'title','summary','when','needs','output','example','boundary'}
                if not isinstance(guide, dict) or set(guide)-allowed or any(not isinstance(v,str) or len(v)>2000 for v in guide.values()):
                    raise ValueError('说明格式无效，每段最多 2000 字')
                updated['guide_override'] = {k:v.strip() for k,v in guide.items() if v.strip()}
            labels[sid] = updated
            atomic(self.labels_path, labels)
            self.labels = labels

    def detail(self, sid):
        with self.lock:
            row = self.state['items'].get(sid)
            if not row or row['status'] != 'active': raise KeyError(sid)
            p = Path(row['path']) / 'SKILL.md'
            if canonical(p.parent) != row['path'].casefold(): raise ValueError('技能路径已变更，请刷新')
            return {'text': p.read_text(encoding='utf-8-sig', errors='replace')[:200000]}
