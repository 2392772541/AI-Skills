from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from skilllib import parse_frontmatter, read_text, NAME_RE


def validate(source: Path) -> tuple[str, list[str]]:
    skill_md = source / "SKILL.md"
    if not skill_md.exists():
        return "", ["SKILL.md does not exist"]
    frontmatter, issues = parse_frontmatter(read_text(skill_md))
    name = str(frontmatter.get("name", ""))
    errors = list(issues)
    if name and not NAME_RE.match(name):
        errors.append("invalid skill name")
    if name and source.name != name:
        errors.append(f"folder {source.name} does not match declared name {name}")
    return name, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely promote a reviewed Skill into the active library.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Actually copy; default is dry-run")
    parser.add_argument("--skip-doctor", action="store_true", help="Skip Skill Doctor pre-promotion audit")
    args = parser.parse_args()
    name, errors = validate(args.source)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2

    # Deterministic Layer 1 Gate: Skill Doctor Audit
    if not args.skip_doctor:
        doctor_script = Path(__file__).resolve().parents[1] / "skills" / "skill-doctor" / "scripts" / "doctor.py"
        if doctor_script.exists():
            print("[GATE] Running Skill Doctor pre-promotion audit...")
            res = subprocess.call([sys.executable, str(doctor_script), "audit", str(args.source.resolve())])
            if res != 0:
                print(f"ERROR: Skill Doctor audit failed with exit code {res}. Resolve issues before promoting.")
                return 2
            print("[GATE] Skill Doctor audit passed.")

    destination = args.destination_root / name
    if destination.exists():
        print(f"ERROR: destination already exists: {destination}")
        return 3
    print(f"source={args.source.resolve()}")
    print(f"destination={destination.resolve()}")
    if not args.apply:
        print("dry-run: no files copied; add --apply after review")
        return 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(args.source, destination)
    print("promoted=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
