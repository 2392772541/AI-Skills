"""Local pre-publish gate for the recurring weekly report workflow."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BAD_DOUYIN = re.compile(r"douyin\.com/video/(?:\d{1,18}(?:\D|$)|\d{20,})")
LEAK = re.compile(r"reconstructed_doc|selected_frames|rapid_crops|ocr_work|link_crops|待核对|链接待补全")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("report_dir", type=Path)
    args = ap.parse_args()
    report = args.report_dir
    doc = (report / "document.md").read_text(encoding="utf-8")
    audit_path = report / "audit_structured.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for key in ("duplicate_urls", "duplicate_titles", "malformed_douyin", "unresolved_items", "screenshot_evidence_issues"):
        if audit.get(key):
            errors.append(f"{key}={len(audit[key])}")
    if BAD_DOUYIN.search(doc):
        errors.append("malformed_douyin_in_document")
    if LEAK.search(doc):
        errors.append("temporary_path_or_review_marker_leak")
    if audit.get("items") != len(re.findall(r"^\d+\. ", doc, re.M)):
        errors.append("audit_item_count_mismatch")
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False))
        return 1
    result = {"ok": True, "items": audit.get("items"), "linked_items": audit.get("linked_items"), "screenshot_fallbacks": audit.get("screenshot_fallbacks", 0)}
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
