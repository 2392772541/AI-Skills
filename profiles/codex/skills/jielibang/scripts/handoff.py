#!/usr/bin/env python3
"""Atomic local task checkpoints for the 接力棒 Codex skill."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

STATUS_VALUES = {"in_progress", "blocked", "complete", "paused", "archived"}


def now_text() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def safe_id(name: str) -> str:
    digest = hashlib.sha256(name.strip().casefold().encode("utf-8")).hexdigest()[:12]
    return f"task-{digest}"


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)


def atomic_write_json(path: Path, data: Any) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def workspace_path(value: str | None) -> Path:
    return Path(value or os.getcwd()).expanduser().resolve()


def store_paths(workspace: Path) -> tuple[Path, Path, Path, Path]:
    root = workspace / ".codex-handoff"
    return root, root / "index.json", root / "tasks", root / "history"


def load_index(index_file: Path, workspace: Path) -> dict[str, Any]:
    if not index_file.exists():
        return {"version": 1, "workspace": str(workspace), "current_task_id": None, "tasks": {}}
    try:
        data = json.loads(index_file.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"交接索引损坏：{index_file}\n{exc}")
    data.setdefault("version", 1)
    data.setdefault("workspace", str(workspace))
    data.setdefault("current_task_id", None)
    data.setdefault("tasks", {})
    return data


def ensure_git_exclude(workspace: Path, root: Path) -> None:
    try:
        result = subprocess.run(
            ["git", "-C", str(workspace), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5
        )
        if result.returncode != 0:
            return
        git_root = Path(result.stdout.strip()).resolve()
        relative = root.resolve().relative_to(git_root).as_posix().rstrip("/") + "/"
        exclude = git_root / ".git" / "info" / "exclude"
        if not exclude.parent.exists():
            return
        existing = exclude.read_text(encoding="utf-8-sig") if exclude.exists() else ""
        line = f"/{relative}"
        if line not in {x.strip() for x in existing.splitlines()}:
            with exclude.open("a", encoding="utf-8") as handle:
                if existing and not existing.endswith("\n"):
                    handle.write("\n")
                handle.write(f"\n# Codex 接力棒本地进度\n{line}\n")
    except Exception:
        # Checkpointing must not fail merely because Git exclusion could not be updated.
        return


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if not isinstance(value, list):
        raise SystemExit("列表字段必须是字符串数组")
    return [str(item).strip() for item in value if str(item).strip()]


def validate_payload(data: dict[str, Any]) -> dict[str, Any]:
    task = str(data.get("task", "")).strip()
    objective = str(data.get("objective", "")).strip()
    if not task:
        raise SystemExit("缺少 task（任务名）")
    if not objective:
        raise SystemExit("缺少 objective（任务目标）")
    status = str(data.get("status", "in_progress")).strip()
    if status not in STATUS_VALUES - {"archived"}:
        raise SystemExit(f"status 必须是：{', '.join(sorted(STATUS_VALUES - {'archived'}))}")
    normalized = {"task": task, "objective": objective, "status": status}
    for key in ("completed", "next", "files", "tests", "blockers", "decisions", "notes"):
        normalized[key] = normalize_list(data.get(key))
    return normalized


def bullets(items: list[str], empty: str = "无") -> str:
    return "\n".join(f"- {item}" for item in items) if items else f"- {empty}"


def render_markdown(task_id: str, workspace: Path, saved_at: str, data: dict[str, Any]) -> str:
    return f'''---
task_id: {task_id}
task: {json.dumps(data["task"], ensure_ascii=False)}
status: {data["status"]}
saved_at: {json.dumps(saved_at, ensure_ascii=False)}
workspace: {json.dumps(str(workspace), ensure_ascii=False)}
---

# {data["task"]}

## 目标

{data["objective"]}

## 已完成

{bullets(data["completed"])}

## 下一步

{bullets(data["next"], "任务已完成或等待新指令")}

## 关键文件

{bullets(data["files"])}

## 测试与验证

{bullets(data["tests"], "尚未运行验证")}

## 阻塞项

{bullets(data["blockers"])}

## 重要决定

{bullets(data["decisions"])}

## 恢复备注

{bullets(data["notes"])}
'''


def resolve_task(index: dict[str, Any], selector: str | None) -> str:
    tasks = index.get("tasks", {})
    if not selector:
        task_id = index.get("current_task_id")
        if not task_id:
            raise SystemExit("当前工作区还没有可恢复的任务。")
        return task_id
    if selector in tasks:
        return selector
    folded = selector.casefold()
    matches = [tid for tid, meta in tasks.items() if str(meta.get("name", "")).casefold() == folded]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise SystemExit(f"任务名不唯一，请使用任务 ID：{selector}")
    raise SystemExit(f"找不到任务：{selector}")


def cmd_init(args: argparse.Namespace) -> int:
    workspace = workspace_path(args.workspace)
    root, index_file, tasks_dir, history_dir = store_paths(workspace)
    tasks_dir.mkdir(parents=True, exist_ok=True)
    history_dir.mkdir(parents=True, exist_ok=True)
    index = load_index(index_file, workspace)
    atomic_write_json(index_file, index)
    ensure_git_exclude(workspace, root)
    print(f"接力棒目录已就绪：{root}")
    return 0


def cmd_save(args: argparse.Namespace) -> int:
    workspace = workspace_path(args.workspace)
    if not workspace.exists() or not workspace.is_dir():
        raise SystemExit(f"工作区不存在：{workspace}")
    source = Path(args.input).expanduser().resolve()
    try:
        raw = json.loads(source.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"无法读取检查点 JSON：{source}\n{exc}")
    data = validate_payload(raw)
    root, index_file, tasks_dir, history_dir = store_paths(workspace)
    tasks_dir.mkdir(parents=True, exist_ok=True)
    history_dir.mkdir(parents=True, exist_ok=True)
    ensure_git_exclude(workspace, root)
    index = load_index(index_file, workspace)
    task_id = safe_id(data["task"])
    saved_at = now_text()
    markdown = render_markdown(task_id, workspace, saved_at, data)
    task_file = tasks_dir / f"{task_id}.md"
    if task_file.exists():
        previous = task_file.read_text(encoding="utf-8-sig")
        if previous != markdown:
            stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
            snapshot = history_dir / task_id / f"{stamp}.md"
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(task_file, snapshot)
    atomic_write_text(task_file, markdown)
    index["workspace"] = str(workspace)
    index["current_task_id"] = task_id
    index["updated_at"] = saved_at
    index["tasks"][task_id] = {
        "name": data["task"], "status": data["status"], "updated_at": saved_at,
        "file": task_file.relative_to(root).as_posix()
    }
    atomic_write_json(index_file, index)
    print(json.dumps({"ok": True, "task_id": task_id, "task": data["task"], "file": str(task_file), "saved_at": saved_at}, ensure_ascii=False))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    workspace = workspace_path(args.workspace)
    root, index_file, _, _ = store_paths(workspace)
    index = load_index(index_file, workspace)
    task_id = resolve_task(index, args.task)
    meta = index["tasks"].get(task_id)
    if not meta:
        raise SystemExit(f"索引中缺少任务：{task_id}")
    task_file = root / meta["file"]
    if not task_file.exists():
        raise SystemExit(f"任务文件丢失：{task_file}")
    sys.stdout.write(task_file.read_text(encoding="utf-8-sig"))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    workspace = workspace_path(args.workspace)
    _, index_file, _, _ = store_paths(workspace)
    index = load_index(index_file, workspace)
    tasks = index.get("tasks", {})
    if not tasks:
        print("当前工作区还没有保存的任务。")
        return 0
    current = index.get("current_task_id")
    rows = sorted(tasks.items(), key=lambda pair: pair[1].get("updated_at", ""), reverse=True)
    for task_id, meta in rows:
        marker = "*" if task_id == current else " "
        print(f"{marker} {task_id} | {meta.get('name')} | {meta.get('status')} | {meta.get('updated_at')}")
    return 0


def cmd_archive(args: argparse.Namespace) -> int:
    workspace = workspace_path(args.workspace)
    _, index_file, _, _ = store_paths(workspace)
    index = load_index(index_file, workspace)
    task_id = resolve_task(index, args.task)
    index["tasks"][task_id]["status"] = "archived"
    index["tasks"][task_id]["updated_at"] = now_text()
    if index.get("current_task_id") == task_id:
        candidates = [(tid, meta) for tid, meta in index["tasks"].items() if tid != task_id and meta.get("status") != "archived"]
        candidates.sort(key=lambda pair: pair[1].get("updated_at", ""), reverse=True)
        index["current_task_id"] = candidates[0][0] if candidates else None
    atomic_write_json(index_file, index)
    print(f"已归档：{index['tasks'][task_id].get('name')} ({task_id})")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    workspace = workspace_path(args.workspace)
    root, index_file, _, _ = store_paths(workspace)
    index = load_index(index_file, workspace)
    errors: list[str] = []
    for task_id, meta in index.get("tasks", {}).items():
        path = root / str(meta.get("file", ""))
        if not path.exists():
            errors.append(f"任务文件不存在：{task_id} -> {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"检查通过：{len(index.get('tasks', {}))} 个任务，当前任务={index.get('current_task_id')}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="接力棒：Codex 本地任务进度保存与恢复")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn in (("init", cmd_init), ("list", cmd_list), ("check", cmd_check)):
        item = sub.add_parser(name)
        item.add_argument("--workspace")
        item.set_defaults(func=fn)
    save = sub.add_parser("save")
    save.add_argument("--workspace")
    save.add_argument("--input", required=True)
    save.set_defaults(func=cmd_save)
    show = sub.add_parser("show")
    show.add_argument("--workspace")
    show.add_argument("--task")
    show.set_defaults(func=cmd_show)
    archive = sub.add_parser("archive")
    archive.add_argument("--workspace")
    archive.add_argument("--task")
    archive.set_defaults(func=cmd_archive)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
