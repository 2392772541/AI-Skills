#!/usr/bin/env python3
"""Audit a reconstructed weekly Markdown report before Feishu publishing."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path


HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
NUMBERED_RE = re.compile(r"^(\d+)\.\s+(.+?)\s*$")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
VALID_DOUYIN_RE = re.compile(r"https://www\.douyin\.com/video/\d{19}")
REVIEW_TIME_RE = re.compile(r"(?:P\d+\s+)?(?:\d{1,2}:)?\d{2}:\d{2}", re.IGNORECASE)
REVIEW_MARKER_RE = re.compile(r"人工复查|manual\s+review", re.IGNORECASE)
NOT_LINK_EVIDENCE_RE = re.compile(r"不作为链接证据|not\s+(?:url|link)\s+evidence", re.IGNORECASE)


def normalize_title(value: str) -> str:
    return "".join(ch.lower() for ch in value if ch.isalnum())


def parse_report(text: str) -> tuple[list[dict], list[str], list[str]]:
    sections: list[str] = []
    subsections: list[str] = []
    items: list[dict] = []
    main = ""
    sub = ""
    current: dict | None = None

    def start_item(raw_title: str) -> None:
        nonlocal current
        match = NUMBERED_RE.match(raw_title)
        current = {
            "main": main,
            "sub": sub,
            "number": match.group(1) if match else "",
            "title": match.group(2) if match else raw_title,
            "primary": [],
            "alternatives": [],
            "images": [],
            "review_text": [],
        }
        items.append(current)

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            value = heading.group(2).strip()
            if level == 2:
                main, sub, current = value, "", None
                sections.append(value)
            elif level == 3:
                if NUMBERED_RE.match(value):
                    start_item(value)
                else:
                    sub, current = value, None
                    subsections.append(f"{main} / {sub}")
            else:
                start_item(value)
            continue

        legacy = NUMBERED_RE.match(line)
        if legacy and main:
            start_item(line)
            continue
        if current is None:
            continue

        image_match = IMAGE_RE.search(line)
        if image_match:
            current["images"].append(image_match.group(1))
            continue

        urls = list(dict.fromkeys(URL_RE.findall(line)))
        if not urls:
            current["review_text"].append(line.lstrip("> "))
            continue
        target = "alternatives" if line.startswith(("备选：", "备选链接：")) else "primary"
        current[target].extend(url for url in urls if url not in current[target])

    return items, sections, subsections


def audit(items: list[dict], sections: list[str], subsections: list[str], threshold: float) -> dict:
    primary_occurrences = [
        (url, item["title"]) for item in items for url in item["primary"]
    ]
    alternative_occurrences = [
        (url, item["title"]) for item in items for url in item["alternatives"]
    ]
    all_occurrences = primary_occurrences + alternative_occurrences
    url_counts = Counter(url for url, _ in all_occurrences)
    duplicate_urls = [url for url, count in url_counts.items() if count > 1]

    normalized = [normalize_title(item["title"]) for item in items]
    title_counts = Counter(normalized)
    duplicate_titles = [title for title, count in title_counts.items() if title and count > 1]

    similar_titles = []
    for index, title in enumerate(normalized):
        for previous in range(index):
            score = SequenceMatcher(None, title, normalized[previous]).ratio()
            if score >= threshold and title != normalized[previous]:
                similar_titles.append(
                    {
                        "score": round(score, 3),
                        "first": items[previous]["title"],
                        "second": items[index]["title"],
                    }
                )

    malformed_douyin = []
    for url, title in all_occurrences:
        if "douyin.com/video/" in url and not VALID_DOUYIN_RE.fullmatch(url):
            malformed_douyin.append({"title": title, "url": url})

    screenshot_items = [
        item for item in items if not item["primary"] and item["images"]
    ]
    unresolved = [
        item for item in items if not item["primary"] and not item["images"]
    ]

    screenshot_path_owners: dict[str, list[str]] = {}
    for item in screenshot_items:
        for image in item["images"]:
            screenshot_path_owners.setdefault(image, []).append(item["title"])
    duplicate_screenshot_paths = [
        {"image": image, "titles": titles}
        for image, titles in screenshot_path_owners.items()
        if len(set(titles)) > 1
    ]

    screenshot_evidence_issues = []
    for item in screenshot_items:
        review_text = " ".join(item["review_text"])
        missing = []
        if not REVIEW_MARKER_RE.search(review_text):
            missing.append("manual-review marker")
        if not REVIEW_TIME_RE.search(review_text):
            missing.append("source timestamp")
        if not NOT_LINK_EVIDENCE_RE.search(review_text):
            missing.append("evidence boundary")
        if missing:
            screenshot_evidence_issues.append(
                {"title": item["title"], "images": item["images"], "missing": missing}
            )

    return {
        "sections": len(sections),
        "subsections": len(subsections),
        "items": len(items),
        "linked_items": sum(bool(item["primary"]) for item in items),
        "primary_links": len(primary_occurrences),
        "alternative_links": len(alternative_occurrences),
        "screenshot_fallbacks": len(screenshot_items),
        "unresolved": len(unresolved),
        "duplicate_urls": duplicate_urls,
        "duplicate_titles": duplicate_titles,
        "high_similarity_titles": similar_titles,
        "malformed_douyin": malformed_douyin,
        "duplicate_screenshot_paths": duplicate_screenshot_paths,
        "screenshot_evidence_issues": screenshot_evidence_issues,
        "screenshot_items": [item["title"] for item in screenshot_items],
        "unresolved_items": [item["title"] for item in unresolved],
        "section_names": sections,
        "subsection_names": subsections,
    }


def render_markdown(result: dict) -> str:
    lines = [
        "# Weekly report audit",
        "",
        f"- Sections: {result['sections']}",
        f"- Subsections: {result['subsections']}",
        f"- Items: {result['items']}",
        f"- Linked items: {result['linked_items']}",
        f"- Primary links: {result['primary_links']}",
        f"- Alternative links: {result['alternative_links']}",
        f"- Screenshot fallbacks: {result['screenshot_fallbacks']}",
        f"- Unresolved: {result['unresolved']}",
        f"- Duplicate URLs: {len(result['duplicate_urls'])}",
        f"- Duplicate titles: {len(result['duplicate_titles'])}",
        f"- High-similarity title pairs: {len(result['high_similarity_titles'])}",
        f"- Malformed Douyin links: {len(result['malformed_douyin'])}",
        f"- Reused screenshot paths: {len(result['duplicate_screenshot_paths'])}",
        f"- Screenshot evidence issues: {len(result['screenshot_evidence_issues'])}",
        "",
        "## Screenshot fallbacks",
        "",
    ]
    lines.extend(f"- {title}" for title in result["screenshot_items"] or ["None"])
    lines.extend(["", "## Reused screenshot paths", ""])
    if result["duplicate_screenshot_paths"]:
        for entry in result["duplicate_screenshot_paths"]:
            lines.append(f"- {entry['image']}: {' <> '.join(entry['titles'])}")
    else:
        lines.append("- None")
    lines.extend(["", "## Screenshot evidence issues", ""])
    if result["screenshot_evidence_issues"]:
        for entry in result["screenshot_evidence_issues"]:
            lines.append(f"- {entry['title']}: {', '.join(entry['missing'])}")
    else:
        lines.append("- None")
    lines.extend(["", "## Unresolved", ""])
    lines.extend(f"- {title}" for title in result["unresolved_items"] or ["None"])
    lines.extend(["", "## Duplicate URLs", ""])
    lines.extend(f"- {url}" for url in result["duplicate_urls"] or ["None"])
    lines.extend(["", "## High-similarity titles", ""])
    if result["high_similarity_titles"]:
        for pair in result["high_similarity_titles"]:
            lines.append(f"- {pair['score']}: {pair['first']} <> {pair['second']}")
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--similarity-threshold", type=float, default=0.90)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    items, sections, subsections = parse_report(args.input.read_text(encoding="utf-8"))
    result = audit(items, sections, subsections, args.similarity_threshold)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    print(payload, end="")
    if args.json_output:
        args.json_output.write_text(payload, encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.write_text(render_markdown(result), encoding="utf-8")
    if args.strict and (
        result["unresolved"]
        or result["duplicate_urls"]
        or result["duplicate_titles"]
        or result["malformed_douyin"]
        or result["duplicate_screenshot_paths"]
        or result["screenshot_evidence_issues"]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
