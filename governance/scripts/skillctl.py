from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

LIBRARY_ROOT = Path(os.environ.get("AI_SKILLS_HOME", str(Path(__file__).resolve().parents[1])))
SCRIPTS = LIBRARY_ROOT / "scripts"
DEFAULT_REGISTRY = LIBRARY_ROOT / "registry" / "skills.json"


def run(script: str, args: list[str]) -> int:
    cmd = [sys.executable, str(SCRIPTS / script), *args]
    print("+", subprocess.list2cmdline(cmd))
    return subprocess.call(cmd)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: skillctl.py <build|audit|route|compare|promote|test|git-sync|git-verify> [args...]")
        return 2
    command, rest = sys.argv[1], sys.argv[2:]
    if command in {"git-sync", "git-verify"}:
        import json
        config_path = LIBRARY_ROOT / "registry" / "portable-local.json"
        if not config_path.exists():
            print("Git portability is not configured on this machine; see repository README.")
            return 2
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        entry = Path(config["repository"]) / "portable" / "skills_portable.py"
        action = ["publish", "--config", config["source_config"]] if command == "git-sync" else ["verify"]
        return subprocess.call([sys.executable, str(entry), *action, *rest])
    defaults = {
        "build": ("build_registry.py", ["--root", str(LIBRARY_ROOT / "skills"), "--root", str(Path.home() / ".codex" / "skills"), "--overrides", str(LIBRARY_ROOT / "registry" / "overrides.json"), "--output", str(DEFAULT_REGISTRY), "--index", str(LIBRARY_ROOT / "skill-index.generated.md")]),
        "audit": ("audit_skills.py", ["--registry", str(DEFAULT_REGISTRY), "--output", str(LIBRARY_ROOT / "_reports" / "skill-audit.json"), "--markdown", str(LIBRARY_ROOT / "_reports" / "skill-audit.md")]),
        "route": ("route_skills.py", ["--registry", str(DEFAULT_REGISTRY)]),
        "compare": ("compare_skills.py", []),
        "promote": ("promote_skill.py", ["--destination-root", str(LIBRARY_ROOT / "skills")]),
        "test": ("run_routing_tests.py", ["--registry", str(DEFAULT_REGISTRY), "--cases", str(LIBRARY_ROOT / "tests" / "routing-cases.json")]),
    }
    if command not in defaults:
        print(f"unknown command: {command}")
        return 2
    script, prefix = defaults[command]
    return run(script, prefix + rest)


if __name__ == "__main__":
    raise SystemExit(main())
