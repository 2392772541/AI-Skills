"""Git-backed skill snapshots. Stdlib only; never runs imported skill code.

export reads live roots without changing them; restore only accepts a new target.
publish is explicit and refuses public repositories. Runtime data stays local.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from functools import lru_cache
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.cache',
             'dist', 'build', 'exports', 'output', 'outputs', 'projects', '.pytest_cache'}
PRIVATE_NAMES = {'.env', 'auth.json', 'credentials.json', 'cookies.json', 'cookies.txt',
                 'token.json', 'tokens.json', '.npmrc', '.pypirc', '.ds_store', 'thumbs.db'}
SKIP_SUFFIXES = {'.pyc', '.pyo', '.log', '.db', '.sqlite', '.sqlite3', '.psd',
                 '.zip', '.7z', '.exe', '.msi', '.key', '.pem', '.p12'}
TOKEN_PATTERNS = [
    ('private-key', re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----')),
    ('provider-token', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|glpat-[A-Za-z0-9_-]{20,})\b')),
    ('cloud-key', re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')),
]
ASSIGN = re.compile(r'''(?im)(?:api[_-]?key|api[_-]?token|access[_-]?token|client[_-]?secret|password)\s*["']?\s*[:=]\s*["']([^"'\r\n]{16,})["']''')

def sha(data): return hashlib.sha256(data).hexdigest()
def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def checked_path(base, rel):
    candidate = base / rel
    if candidate.resolve() == base.resolve() or not candidate.resolve().is_relative_to(base.resolve()):
        raise ValueError('Path escapes target: '+str(rel))
    return candidate
def safe_remove(base, p):
    checked_path(base, p.relative_to(base))
    if p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()):
        raise ValueError('Refusing recursive removal of a link: '+str(p))
    if p.is_dir(): shutil.rmtree(p)
    elif p.exists(): p.unlink()
def secret_findings(data):
    try: text=data.decode('utf-8-sig')
    except UnicodeDecodeError: return []
    found=[name for name, pattern in TOKEN_PATTERNS if pattern.search(text)]
    for m in ASSIGN.finditer(text):
        val=m.group(1)
        if re.fullmatch(r'[A-Za-z0-9_+./=-]{20,}', val) and not any(w in val.lower() for w in
            ('example','placeholder','your','test','dummy','process','environ','secret','password','token','xxxx')):
            found.append('credential-literal')
    return sorted(set(found))
@lru_cache(maxsize=1)
def public_reviews():
    reviews=REPO/'portable/reviewed-public-identifiers.json'
    return read(reviews) if reviews.exists() else {}
def reviewed_findings(rel, data):
    findings=secret_findings(data)
    item=public_reviews().get(rel)
    if item and sha(data)==item['sha256']:
        findings=[rule for rule in findings if rule not in item['rules']]
    return findings
def walk(root):
    def descend(p, rel, seen):
        actual=p.resolve()
        if actual in seen: raise ValueError('Link cycle: '+str(p))
        if p.is_dir():
            if p.name in SKIP_DIRS: return
            for child in sorted(p.iterdir()):
                yield from descend(child, rel/child.name, seen|{actual})
        elif p.is_file(): yield p,rel
    yield from descend(root,Path(),set())
def reason(p):
    if p.name.lower() in PRIVATE_NAMES or (p.name.startswith('.env') and p.name not in {'.env.example','.env.template'}): return 'local-credentials-or-state'
    if p.suffix.lower() in SKIP_SUFFIXES: return 'runtime-or-generated-artifact'
    if p.stat().st_size > 40*1024*1024: return 'large-artifact'
    return None

def source_groups(config):
    library=Path(config['library']).resolve()
    groups=[('shared',library/'skills','skills'),('codex',Path(config['codex']),'profiles/codex/skills'),
            ('cursor',Path(config['cursor']),'profiles/cursor/skills')]
    for item in ('scripts','tests','web'):
        groups.append(('governance-'+item,library/item,'governance/'+item))
    return groups

def export(config_path):
    config=read(config_path)
    stage=Path(tempfile.mkdtemp(prefix='skills-portable-export-'))
    manifest={'schema':1,'files':{},'excluded':[],'excluded_directory_names':sorted(SKIP_DIRS),'native_managed':[], 'groups':{}, 'relocations':config.get('relocations',[])}
    findings=[]
    for key,src,dest in source_groups(config):
        if not src.is_dir(): raise ValueError('Missing source: '+str(src))
        count=0
        for p,rel in walk(src):
            # System-provided skill versions are installed by Codex, not activated here.
            if key=='codex' and rel.parts and rel.parts[0]=='.system':
                if p.name=='SKILL.md': manifest['native_managed'].append(rel.as_posix())
                continue
            why=reason(p)
            out=(Path(dest)/rel).as_posix()
            if why:
                manifest['excluded'].append({'path':out,'reason':why});continue
            data=p.read_bytes()
            issues=reviewed_findings(out,data)
            if issues: findings.append({'path':out,'rules':issues})
            target=checked_path(stage,out);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            manifest['files'][out]={'sha256':sha(data),'bytes':len(data)}
            count+=1
        manifest['groups'][key]=count
    overrides=Path(config['library'])/'registry/overrides.json'
    data=overrides.read_bytes(); name='governance/registry/overrides.json'
    issues=secret_findings(data)
    if issues:findings.append({'path':name,'rules':issues})
    target=checked_path(stage,name);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    manifest['files'][name]={'sha256':sha(data),'bytes':len(data)}
    if findings:
        dump(REPO/'.local/secret-findings.json',findings)
        raise ValueError(f'Export blocked: {len(findings)} files need secret review; paths/rules only in .local/secret-findings.json. Stage retained locally.')
    # Commit snapshot content only after capture and scan completed successfully.
    for top in ('skills','profiles','governance'):
        target=REPO/top
        if target.exists():safe_remove(REPO,target)
        shutil.copytree(stage/top,target)
    dump(REPO/'portable/manifest.json',manifest)
    safe_remove(stage.parent,stage)
    verify()
    print(json.dumps({'exported':len(manifest['files']),'groups':manifest['groups'],'excluded_files':len(manifest['excluded'])}))

def verify():
    manifest=read(REPO/'portable/manifest.json')
    issues=[]
    for rel,entry in manifest['files'].items():
        p=checked_path(REPO,rel)
        if not p.is_file() or sha(p.read_bytes())!=entry['sha256']: issues.append(rel)
        elif reviewed_findings(rel,p.read_bytes()): issues.append(rel+' (secret)')
    expected=set(manifest['files'])
    actual={p.relative_to(REPO).as_posix() for top in ('skills','profiles','governance') for p in (REPO/top).rglob('*') if p.is_file()}
    issues.extend(sorted(actual-expected))
    if issues: raise ValueError(f'Verification failed: {len(issues)} entries; first paths: {issues[:5]}')
    print(f'verified files={len(expected)}')

def replacements(target, manifest):
    result=[]
    for item in manifest.get('relocations',[]):
        new=str(target/item['target'])
        old=item['from']
        for a,b in ((old,new),(old.replace('\\','/'),new.replace('\\','/')),(old.replace('\\','\\\\'),new.replace('\\','\\\\'))):
            result.append((a,b))
    return sorted(result,key=lambda pair:len(pair[0]),reverse=True)

def restore(target, relocate):
    verify();target=target.resolve()
    if target.exists():raise ValueError('Restore target must not exist; refusing to overwrite existing skills: '+str(target))
    manifest=read(REPO/'portable/manifest.json')
    target.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='skills-restore-',dir=target.parent))
    outputs={}; changed=[]
    try:
        for rel,entry in manifest['files'].items():
            if rel.startswith('skills/'): out='library/'+rel
            elif rel.startswith('profiles/codex/skills/'): out='user/.codex/skills/'+rel.removeprefix('profiles/codex/skills/')
            elif rel.startswith('profiles/cursor/skills/'): out='user/.cursor/skills/'+rel.removeprefix('profiles/cursor/skills/')
            else: out='library/'+rel.removeprefix('governance/')
            data=(REPO/rel).read_bytes()
            if relocate:
                try:
                    text=data.decode('utf-8')
                    for old,new in replacements(target,manifest):text=text.replace(old,new)
                    if text.encode('utf-8')!=data:changed.append(out)
                    data=text.encode('utf-8')
                except UnicodeDecodeError:pass
            p=checked_path(stage,out);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            outputs[out]=sha(data)
        # Claude/agents receive the same shared payload as today, as ordinary dirs.
        for tool in ('.claude','.agents'):
            dest=stage/'user'/tool/'skills'
            shutil.copytree(stage/'library/skills',dest)
            for p in dest.rglob('*'):
                if p.is_file():outputs[p.relative_to(stage).as_posix()]=sha(p.read_bytes())
        for rel,digest in outputs.items():
            if sha((stage/rel).read_bytes())!=digest:raise ValueError('Restore verification failed: '+rel)
        dump(stage/'restore-receipt.json',{'files':outputs,'relocated':changed,'source_manifest':sha((REPO/'portable/manifest.json').read_bytes())})
        stage.rename(target)
    except Exception:
        # Keep failed staging tree as forensic evidence; never delete user directories.
        raise
    print(json.dumps({'restored_files':len(outputs),'relocated_files':len(changed),'target':str(target)}))

def git(*args):
    return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf-8').strip()
def install(bundle, user_root):
    """Activate an already verified bundle; never overwrite a differing file."""
    bundle=bundle.resolve();user_root=user_root.absolute()
    receipt=read(bundle/'restore-receipt.json')
    plan=[]
    for rel,digest in receipt['files'].items():
        src=checked_path(bundle,rel)
        if not src.is_file() or sha(src.read_bytes())!=digest:raise ValueError('Bundle changed: '+rel)
        if not rel.startswith('user/'):continue
        dest=user_root/rel.removeprefix('user/')
        checked_path(user_root,rel.removeprefix('user/'))
        for ancestor in [dest,*dest.parents]:
            if ancestor.is_symlink() or (hasattr(ancestor,'is_junction') and ancestor.is_junction()):
                raise ValueError('Refusing installation through a link: '+str(ancestor))
        data=src.read_bytes()
        try:
            text=data.decode('utf-8')
            old=str(bundle/'user');new=str(user_root)
            for a,b in ((old.replace('\\','\\\\'),new.replace('\\','\\\\')),(old.replace('\\','/'),new.replace('\\','/')),(old,new)):
                text=text.replace(a,b)
            data=text.encode('utf-8')
        except UnicodeDecodeError:pass
        if dest.exists():
            if not dest.is_file() or dest.read_bytes()!=data:raise ValueError('Local conflict; nothing installed: '+str(dest))
        else:plan.append((dest,data))
    # Full preflight above completes before the first write.
    created=[]
    for dest,data in plan:
        dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb') as stream:stream.write(data)
        created.append({'path':str(dest),'sha256':sha(data)})
    dump(bundle/'install-receipt.json',{'created':created,'user_root':str(user_root)})
    print('installed_files='+str(len(created)))
def publish(config):
    if config: export(config)
    verify()
    remote=git('remote','get-url','origin')
    m=re.fullmatch(r'https://github.com/([\w.-]+/[\w.-]+?)(?:\.git)?',remote)
    if not m:raise ValueError('Expected a GitHub HTTPS origin without credentials')
    info=json.loads(subprocess.check_output(['gh','api','repos/'+m[1]],text=True,encoding='utf-8'))
    if not info.get('private'):raise ValueError('Publish refused: repository must be private')
    # No add -A across unreviewed local outputs: only these managed paths.
    git('add','--','skills','profiles','governance','portable','README.md','.gitignore','.gitattributes')
    staged=git('diff','--cached','--name-only','--diff-filter=ACMRT').splitlines()
    for rel in staged:
        p=checked_path(REPO,rel)
        if p.is_file() and reviewed_findings(rel,p.read_bytes()):raise ValueError('Publish blocked by secret scan: '+rel)
    if git('diff','--cached','--name-only'):
        git('commit','-m','Update portable skills and verified restore tooling')
    subprocess.run(['git','-C',str(REPO),'push','origin','HEAD:main'],check=True)
    actual=git('ls-remote','origin','refs/heads/main').split()[0]
    if actual!=git('rev-parse','HEAD'):raise ValueError('Remote revision verification failed')
    print('published='+actual)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest='command',required=True)
    ex=sub.add_parser('export');ex.add_argument('--config',type=Path,required=True)
    sub.add_parser('verify')
    rs=sub.add_parser('restore');rs.add_argument('--target',type=Path,required=True);rs.add_argument('--relocate',action='store_true')
    ins=sub.add_parser('install');ins.add_argument('--bundle',type=Path,required=True);ins.add_argument('--user-root',type=Path,required=True)
    pb=sub.add_parser('publish');pb.add_argument('--config',type=Path)
    args=ap.parse_args()
    if args.command=='export':export(args.config)
    elif args.command=='verify':verify()
    elif args.command=='restore':restore(args.target,args.relocate)
    elif args.command=='install':install(args.bundle,args.user_root)
    elif args.command=='publish':publish(args.config)
if __name__=='__main__':
    try:main()
    except Exception as exc:print(str(exc),file=sys.stderr);sys.exit(1)
