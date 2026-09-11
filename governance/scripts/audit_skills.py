from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from skilllib import load_registry, write_json, utc_now

CRITICAL = {"missing-frontmatter", "invalid-frontmatter", "missing-name", "missing-description", "invalid-name"}
WARNING = {"name-folder-mismatch", "backup-in-active-root", "large-skill-md", "missing-local-links"}


def build_audit(registry: dict) -> dict:
    findings = []
    for entry in registry.get("entries", []):
        for issue in entry.get("issues", []):
            severity = "critical" if issue in CRITICAL else "warning" if issue in WARNING else "info"
            findings.append({"severity": severity, "code": issue, "skill": entry["name"], "path": entry["path"]})
    for duplicate in registry.get("duplicates", []):
        findings.append({
            "severity": "warning",
            "code": "duplicate-exact" if duplicate["exact_content"] else "duplicate-divergent",
            "skill": duplicate["name"],
            "paths": duplicate["paths"],
        })
    counts = Counter(finding["severity"] for finding in findings)
    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "summary": {"critical": counts["critical"], "warning": counts["warning"], "info": counts["info"], "total": len(findings)},
        "findings": findings,
    }


def to_markdown(audit: dict) -> str:
    summary = audit["summary"]
    lines = [
        "# Skill Library Audit", "",
        f"Generated: {audit['generated_at']}",
        f"Critical: {summary['critical']}; warnings: {summary['warning']}; info: {summary['info']}", "",
        "| Severity | Code | Skill | Path |", "|---|---|---|---|",
    ]
    for finding in audit["findings"]:
        paths = finding.get("path") or "<br>".join(finding.get("paths", []))
        lines.append(f"| {finding['severity']} | `{finding['code']}` | `{finding['skill']}` | `{paths}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit an Agent Skills registry.")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--strict", action="store_true", help="Return non-zero for critical findings")
    args = parser.parse_args()
    audit = build_audit(load_registry(args.registry))
    if args.output:
        write_json(args.output, audit)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(to_markdown(audit), encoding="utf-8")
    summary = audit["summary"]
    print(f"critical={summary['critical']} warning={summary['warning']} info={summary['info']} total={summary['total']}")
    return 2 if args.strict and summary["critical"] else 0


if __name__ == "__main__":
    raise SystemExit(main())