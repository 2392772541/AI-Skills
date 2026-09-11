from __future__ import annotations

import argparse
import json
from pathlib import Path
from skilllib import load_registry
from route_skills import route


def main() -> int:
    ap = argparse.ArgumentParser(description="Run deterministic routing regression cases.")
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--cases", type=Path, required=True)
    args = ap.parse_args()
    registry = load_registry(args.registry)
    cases = json.loads(args.cases.read_text(encoding="utf-8-sig"))
    failures = []
    for case in cases:
        results = route(registry, case["query"], limit=5)
        names = [x["name"] for x in results]
        expected = case["expected_top1"]
        forbidden = case.get("forbidden_top1", [])
        ok = bool(names) and names[0] == expected and (not names or names[0] not in forbidden)
        print(f"{'PASS' if ok else 'FAIL'} | {case['query']} | expected={expected} actual={names[:3]}")
        if not ok:
            failures.append({"case": case, "actual": names})
    print(f"cases={len(cases)} passed={len(cases)-len(failures)} failed={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
