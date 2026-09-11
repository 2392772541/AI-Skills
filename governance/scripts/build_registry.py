from __future__ import annotations

import argparse
from pathlib import Path
from skilllib import discover_skills, load_overrides, write_json, active_preferred_entries


def markdown_index(registry: dict) -> str:
    rows = [
        "# AI Skills Generated Registry",
        "",
        f"Generated: {registry['generated_at']}",
        f"Entries: {registry['entry_count']}; unique names: {registry['unique_name_count']}; duplicate names: {registry['duplicate_name_count']}",
        "",
        "| Skill | Categories | Status | Issues | Path |",
        "|---|---|---|---|---|",
    ]
    for entry in active_preferred_entries(registry):
        issues = ", ".join(entry["issues"]) or "ok"
        rows.append(f"| `{entry['name']}` | {', '.join(entry['categories'])} | {entry['status']} | {issues} | `{entry['path']}` |")
    rows += ["", "## Duplicate names", ""]
    if not registry["duplicates"]:
        rows.append("None.")
    for duplicate in registry["duplicates"]:
        kind = "exact content" if duplicate["exact_content"] else "divergent content"
        rows.append(f"### `{duplicate['name']}` - {duplicate['count']} copies, {kind}")
        rows.extend(f"- `{path}`" for path in duplicate["paths"])
        rows.append("")
    return "\n".join(rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a machine-readable registry for local Agent Skills.")
    parser.add_argument("--root", action="append", required=True, help="Skill root to scan; may be repeated")
    parser.add_argument("--overrides", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--index", type=Path)
    args = parser.parse_args()
    registry = discover_skills([Path(value) for value in args.root], load_overrides(args.overrides))
    write_json(args.output, registry)
    if args.index:
        args.index.parent.mkdir(parents=True, exist_ok=True)
        args.index.write_text(markdown_index(registry), encoding="utf-8")
    print(f"registry={args.output} entries={registry['entry_count']} unique={registry['unique_name_count']} duplicates={registry['duplicate_name_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())