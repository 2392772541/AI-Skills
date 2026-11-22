from __future__ import annotations

import json
import mimetypes
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from personal import Catalog

ROOT = Path(os.environ.get("AI_SKILLS_HOME", r"D:\AI-Skills"))
WEB_ROOT = ROOT / "web"
STATIC_ROOT = WEB_ROOT / "static"
REGISTRY = ROOT / "registry" / "skills.json"
AUDIT = ROOT / "_reports" / "skill-audit.json"
GOVERNANCE_STATUS = ROOT / "_logs" / "governance-status.json"
SCRIPTS = ROOT / "scripts"
LOG_DIR = ROOT / "_logs"
LOG_FILE = LOG_DIR / "web-console.log"
HOST = os.environ.get("AI_SKILLS_WEB_HOST", "127.0.0.1")
PORT = int(os.environ.get("AI_SKILLS_WEB_PORT", "8765"))
STARTED_AT = datetime.now().astimezone().isoformat(timespec="seconds")
ACTION_LOCK = threading.Lock()
PERSONAL = Catalog()

LOG_DIR.mkdir(parents=True, exist_ok=True)


def log(message: str) -> None:
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {message}\n"
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(line)


def load_json(path: Path, default):
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return default


def json_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def run_python(script: str, args: list[str], timeout: int = 120) -> dict:
    cmd = [sys.executable, str(SCRIPTS / script), *args]
    started = time.monotonic()
    completed = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"},
    )
    return {
        "ok": completed.returncode == 0,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "duration_ms": round((time.monotonic() - started) * 1000),
        "command": subprocess.list2cmdline(cmd),
    }


def overview() -> dict:
    registry = load_json(REGISTRY, {})
    audit = load_json(AUDIT, {})
    status = load_json(GOVERNANCE_STATUS, {})
    entries = registry.get("entries", [])
    categories: dict[str, int] = {}
    active = 0
    system = 0
    for entry in entries:
        if entry.get("status") == "active":
            active += 1
        if entry.get("is_system"):
            system += 1
        for category in entry.get("categories", []):
            categories[category] = categories.get(category, 0) + 1
    return {
        "registry": {
            "entries": registry.get("entry_count", len(entries)),
            "unique": registry.get("unique_name_count", 0),
            "duplicates": registry.get("duplicate_name_count", 0),
            "active": active,
            "system": system,
            "generated_at": registry.get("generated_at"),
        },
        "audit": audit.get("summary", {"critical": 0, "warning": 0, "info": 0, "total": 0}),
        "governance": status,
        "categories": sorted(
            ({"name": name, "count": count} for name, count in categories.items()),
            key=lambda item: (-item["count"], item["name"]),
        ),
        "server": {"started_at": STARTED_AT, "host": HOST, "port": PORT, "pid": os.getpid()},
    }


def skill_rows(query: str = "", category: str = "", issue: str = "", limit: int = 250) -> list[dict]:
    registry = load_json(REGISTRY, {})
    rows = registry.get("entries", [])
    needle = query.casefold().strip()
    result = []
    for row in rows:
        haystack = " ".join(
            [
                str(row.get("name", "")),
                str(row.get("description", "")),
                " ".join(row.get("aliases", [])),
                " ".join(row.get("triggers", [])),
            ]
        ).casefold()
        if needle and needle not in haystack:
            continue
        if category and category not in row.get("categories", []):
            continue
        if issue and issue not in row.get("issues", []):
            continue
        result.append(
            {
                "id": row.get("id"),
                "name": row.get("name"),
                "description": row.get("description"),
                "path": row.get("path"),
                "root": row.get("root"),
                "categories": row.get("categories", []),
                "issues": row.get("issues", []),
                "status": row.get("status", "active"),
                "priority": row.get("priority", 0),
                "file_count": row.get("file_count", 0),
                "byte_size": row.get("byte_size", 0),
                "is_system": row.get("is_system", False),
            }
        )
        if len(result) >= limit:
            break
    return result


def parse_route_output(text: str) -> list[dict]:
    results = []
    pattern = re.compile(r"^(\d+)\.\s+(\S+)\s+score=(\d+)\s+reasons=(.*?)\s+path=(.*)$")
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if match:
            results.append(
                {
                    "rank": int(match.group(1)),
                    "name": match.group(2),
                    "score": int(match.group(3)),
                    "reasons": match.group(4),
                    "path": match.group(5),
                }
            )
    return results


class Handler(BaseHTTPRequestHandler):
    server_version = "AI-Skills-Console/1.0"

    def log_message(self, fmt: str, *args) -> None:
        log(f"HTTP {self.address_string()} {fmt % args}")

    def send_json(self, value, status: int = 200) -> None:
        body = json_bytes(value)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: Path) -> None:
        try:
            body = path.read_bytes()
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8" if content_type.startswith("text/") or content_type == "application/javascript" else content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 65536:
            raise ValueError("request body too large")
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:
        if self.headers.get('Host', '').split(':')[0] not in {'127.0.0.1', 'localhost'}:
            self.send_json({'error': '仅允许本机访问'}, 403)
            return
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        if path == '/api/personal':
            self.send_json(PERSONAL.snapshot())
            return
        if path == '/api/personal/detail':
            try:
                self.send_json(PERSONAL.detail(params.get('id', [''])[0]))
            except (KeyError, ValueError, OSError) as exc:
                self.send_json({'error': str(exc)}, 404)
            return
        if path == '/legacy':
            self.send_file(STATIC_ROOT / 'index.html')
            return
        if path == "/api/health":
            self.send_json({"ok": True, "pid": os.getpid(), "started_at": STARTED_AT})
            return
        if path == "/api/overview":
            self.send_json(overview())
            return
        if path == "/api/skills":
            query = params.get("q", [""])[0]
            category = params.get("category", [""])[0]
            issue = params.get("issue", [""])[0]
            try:
                limit = max(1, min(500, int(params.get("limit", ["250"])[0])))
            except ValueError:
                limit = 250
            rows = skill_rows(query, category, issue, limit)
            self.send_json({"count": len(rows), "items": rows})
            return
        if path == "/api/duplicates":
            registry = load_json(REGISTRY, {})
            self.send_json({"items": registry.get("duplicates", [])})
            return
        if path == "/api/findings":
            audit = load_json(AUDIT, {})
            self.send_json({"summary": audit.get("summary", {}), "items": audit.get("findings", [])})
            return
        if path == "/":
            self.send_file(STATIC_ROOT / "personal.html")
            return
        candidate = (STATIC_ROOT / path.lstrip("/")).resolve()
        if STATIC_ROOT.resolve() not in candidate.parents:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        self.send_file(candidate)

    def do_POST(self) -> None:
        host = self.headers.get('Host', '')
        origin = self.headers.get('Origin')
        if host.split(':')[0] not in {'127.0.0.1', 'localhost'} or (origin and origin != 'http://' + host) or self.headers.get('Sec-Fetch-Site') == 'cross-site':
            self.send_json({'error': '拒绝跨站请求'}, 403)
            return
        parsed = urlparse(self.path)
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == '/api/personal/scan':
            ok = PERSONAL.scan()
            self.send_json({'ok': ok, 'monitor': PERSONAL.snapshot()['monitor']}, 200 if ok else 503)
            return
        if parsed.path == '/api/personal/label':
            try:
                if not isinstance(payload, dict): raise ValueError('请求格式无效')
                PERSONAL.annotate(payload.get('id', ''), payload)
                self.send_json({'ok': True})
            except (KeyError, ValueError, OSError) as exc:
                self.send_json({'error': str(exc)}, 400)
            return

        if parsed.path == "/api/route":
            query = str(payload.get("query", "")).strip()
            if not query:
                self.send_json({"ok": False, "error": "请输入任务描述"}, HTTPStatus.BAD_REQUEST)
                return
            result = run_python("route_skills.py", ["--registry", str(REGISTRY), query], timeout=30)
            result["items"] = parse_route_output(result["stdout"])
            self.send_json(result, HTTPStatus.OK if result["ok"] else HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if parsed.path in {"/api/refresh", "/api/verify"}:
            if not ACTION_LOCK.acquire(blocking=False):
                self.send_json({"ok": False, "error": "已有治理任务正在运行"}, HTTPStatus.CONFLICT)
                return
            try:
                if parsed.path == "/api/refresh":
                    build = run_python(
                        "build_registry.py",
                        [
                            "--root", str(ROOT / "skills"),
                            "--root", str(Path.home() / ".codex" / "skills"),
                            "--overrides", str(ROOT / "registry" / "overrides.json"),
                            "--output", str(REGISTRY),
                            "--index", str(ROOT / "skill-index.generated.md"),
                        ],
                    )
                    audit = run_python(
                        "audit_skills.py",
                        ["--registry", str(REGISTRY), "--output", str(AUDIT), "--markdown", str(ROOT / "_reports" / "skill-audit.md")],
                    )
                    ok = build["ok"] and audit["ok"]
                    self.send_json({"ok": ok, "build": build, "audit": audit, "overview": overview()}, HTTPStatus.OK if ok else HTTPStatus.INTERNAL_SERVER_ERROR)
                else:
                    cmd = [
                        os.environ.get("COMSPEC", r"C:\Windows\System32\cmd.exe"),
                        "/d", "/s", "/c",
                        f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{ROOT / "verify-governance.ps1"}"',
                    ]
                    started = time.monotonic()
                    completed = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, env={**os.environ, "AI_SKILLS_PYTHON": sys.executable, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
                    result = {"ok": completed.returncode == 0, "exit_code": completed.returncode, "stdout": completed.stdout.strip(), "stderr": completed.stderr.strip(), "duration_ms": round((time.monotonic() - started) * 1000)}
                    self.send_json(result, HTTPStatus.OK if result["ok"] else HTTPStatus.INTERNAL_SERVER_ERROR)
            finally:
                ACTION_LOCK.release()
            return

        self.send_error(HTTPStatus.NOT_FOUND)


def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    PERSONAL.start()
    server.daemon_threads = True
    log(f"START host={HOST} port={PORT} pid={os.getpid()} python={sys.executable}")
    print(f"技能管家网页：http://{HOST}:{PORT}")
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        PERSONAL.stop.set()
        server.server_close()
        log("STOP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
