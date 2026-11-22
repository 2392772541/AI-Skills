from __future__ import annotations

import argparse
import difflib
import hashlib
from pathlib import Path


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two Skill directories without modifying them.")
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    for path in (args.left, args.right):
        if not (path / "SKILL.md").exists():
            parser.error(f"SKILL.md not found under {path}")
    left_text = (args.left / "SKILL.md").read_text(encoding="utf-8-sig", errors="replace").splitlines()
    right_text = (args.right / "SKILL.md").read_text(encoding="utf-8-sig", errors="replace").splitlines()
    diff = "\n".join(difflib.unified_diff(left_text, right_text, fromfile=str(args.left), tofile=str(args.right), lineterm=""))
    left_files = {path.relative_to(args.left).as_posix() for path in args.left.rglob("*") if path.is_file()}
    right_files = {path.relative_to(args.right).as_posix() for path in args.right.rglob("*") if path.is_file()}
    report = [
        "# Skill Comparison", "",
        f"Left: `{args.left.resolve()}`", f"Right: `{args.right.resolve()}`", "",
        f"Trees identical: {'yes' if tree_hash(args.left) == tree_hash(args.right) else 'no'}", "",
        "## Left-only files", *([f"- `{item}`" for item in sorted(left_files-right_files)] or ["None"]), "",
        "## Right-only files", *([f"- `{item}`" for item in sorted(right_files-left_files)] or ["None"]), "",
        "## SKILL.md diff", "", "```diff", diff or "No differences", "```", "",
    ]
    text = "\n".join(report)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())