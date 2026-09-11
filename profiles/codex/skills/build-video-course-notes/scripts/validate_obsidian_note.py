from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


EMBED_PATTERN = re.compile(r"!\[\[([^\]#|]+)(?:[|#][^\]]*)?\]\]")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("vault_root", type=Path)
    parser.add_argument("note", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    vault = args.vault_root.resolve()
    note = args.note.resolve()
    if not note.is_file():
        raise SystemExit(f"Note does not exist: {note}")
    try:
        note.relative_to(vault)
    except ValueError as error:
        raise SystemExit(f"Note is outside vault root: {note}") from error

    text = note.read_text(encoding="utf-8-sig")
    embeds = [match.strip() for match in EMBED_PATTERN.findall(text)]
    resolved = []
    missing = []
    for embed in embeds:
        target = (vault / Path(embed.replace("/", "\\"))).resolve()
        row = {"embed": embed, "target": str(target), "exists": target.is_file()}
        resolved.append(row)
        if not row["exists"]:
            missing.append(row)

    fence_markers = len(re.findall(r"(?m)^```", text))
    result = {
        "note": str(note),
        "vault_root": str(vault),
        "characters": len(text),
        "lines": len(text.splitlines()),
        "frontmatter": text.startswith("---\n") or text.startswith("---\r\n"),
        "embed_count": len(embeds),
        "missing_embed_count": len(missing),
        "missing_embeds": missing,
        "code_fence_markers": fence_markers,
        "code_fences_balanced": fence_markers % 2 == 0,
        "resolved_embeds": resolved,
    }

    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered + "\n", encoding="utf-8")

    if (
        not result["frontmatter"]
        or result["missing_embed_count"]
        or not result["code_fences_balanced"]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
