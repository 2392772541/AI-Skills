from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from skilllib import load_registry, active_preferred_entries


def score_entry(query: str, entry: dict) -> tuple[int, list[str]]:
    normalized = query.lower().strip()
    score = 0
    matched = False
    reasons = []
    for trigger in entry.get("triggers", []):
        token = trigger.lower()
        if token and token in normalized:
            score += 50 + min(len(token), 20)
            matched = True
            reasons.append(f"trigger:{trigger}")
    for pattern in entry.get("patterns", []):
        try:
            if re.search(pattern, query, re.IGNORECASE):
                score += 60
                matched = True
                reasons.append(f"pattern:{pattern}")
        except re.error:
            continue
    for alias in entry.get("aliases", []):
        token = alias.lower()
        if token and token in normalized:
            score += 35
            matched = True
            reasons.append(f"alias:{alias}")
    name_tokens = [token for token in re.split(r"[-_\s]+", entry["name"].lower()) if len(token) > 2]
    for token in name_tokens:
        if token in normalized:
            score += 12
            matched = True
            reasons.append(f"name:{token}")
    description = entry.get("description", "").lower()
    stopwords = {"skill", "skills", "agent", "agents", "using", "use", "with", "from", "this", "that"}
    for token in set(re.findall(r"[a-zA-Z][a-zA-Z0-9+.-]{2,}", normalized)) - stopwords:
        if token.lower() in description:
            score += 4
            matched = True
    if matched:
        score += int(entry.get("priority", 0))
    return score, reasons


def route(registry: dict, query: str, limit: int = 5) -> list[dict]:
    ranked = []
    for entry in active_preferred_entries(registry):
        score, reasons = score_entry(query, entry)
        if score > 0:
            ranked.append({"name": entry["name"], "score": score, "path": entry["path"], "reasons": reasons, "categories": entry.get("categories", [])})
    ranked.sort(key=lambda item: (-item["score"], item["name"]))
    return ranked[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a natural-language task to likely local Skills.")
    parser.add_argument("query")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = route(load_registry(args.registry), args.query, args.limit)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for index, result in enumerate(results, 1):
            print(f"{index}. {result['name']} score={result['score']} reasons={','.join(result['reasons']) or '-'} path={result['path']}")
    return 0 if results else 3


if __name__ == "__main__":
    raise SystemExit(main())