#!/usr/bin/env python3
"""Validate the structural parts of an Obsidian learning note.

No third-party packages are required. This is a gate, not a semantic fact checker.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = ("本节学习目标", "关键结论", "详细笔记", "坑点与隐患", "待确认项")
EMBED_RE = re.compile(r"!\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("note", type=Path)
    parser.add_argument("--vault-root", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.note.is_file():
        print(f"ERROR: note not found: {args.note}")
        return 2
    text = args.note.read_text(encoding="utf-8")
    errors: list[str] = []

    if not text.startswith("---\n"):
        errors.append("frontmatter must start at the first line")
    elif "\n---\n" not in text[4:]:
        errors.append("frontmatter closing delimiter is missing")

    if len(re.findall(r"^```", text, flags=re.MULTILINE)) % 2:
        errors.append("fenced code blocks are unbalanced")
    for heading in REQUIRED_HEADINGS:
        if not re.search(rf"^##\s+{re.escape(heading)}\s*$", text, flags=re.MULTILINE):
            errors.append(f"missing heading: {heading}")

    if args.vault_root:
        root = args.vault_root.resolve()
        for raw in EMBED_RE.findall(text):
            target = (root / raw).resolve()
            try:
                target.relative_to(root)
            except ValueError:
                errors.append(f"embed escapes vault root: {raw}")
                continue
            if not target.is_file():
                errors.append(f"missing embed: {raw}")

    uncertain = len(re.findall(r"待确认", text))
    anchors = len(
        re.findall(
            r"\[(?:(?:P\d+|D\d{2}-(?:AM\d?|PM))\s+)?\d{1,2}:\d{2}|\[DOCX\s+p\.\d+|\[原稿第\s*\d+\s*段",
            text,
        )
    )
    print(f"note={args.note}")
    print(f"uncertain_markers={uncertain}")
    print(f"source_anchors={anchors}")
    print(f"embeds={len(EMBED_RE.findall(text))}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
