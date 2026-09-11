from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

home = Path(os.environ.get("AI_SKILLS_HOME", r"D:\AI-Skills"))
entry = home / "scripts" / "skillctl.py"
if not entry.exists():
    raise SystemExit(f"Skill governance entry not found: {entry}")
raise SystemExit(subprocess.call([sys.executable, str(entry), *sys.argv[1:]]))
