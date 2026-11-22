from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from skilllib import discover_skills, parse_frontmatter
from route_skills import route
from audit_skills import build_audit


class SkillGovernanceTests(unittest.TestCase):
    def make_skill(self, root: Path, name: str, description: str = "Test skill") -> Path:
        path = root / name
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n", encoding="utf-8")
        return path

    def test_frontmatter_parser(self):
        frontmatter, issues = parse_frontmatter("---\nname: demo-skill\ndescription: >\n  Does a useful thing.\n---\n")
        self.assertEqual("demo-skill", frontmatter["name"])
        self.assertIn("useful", frontmatter["description"])
        self.assertEqual([], issues)

    def test_duplicate_detection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            left, right = base / "left", base / "right"
            self.make_skill(left, "same-skill")
            self.make_skill(right, "same-skill", "Different")
            registry = discover_skills([left, right])
            self.assertEqual(1, registry["duplicate_name_count"])
            self.assertFalse(registry["duplicates"][0]["exact_content"])

    def test_audit_critical(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "broken"
            path.mkdir()
            (path / "SKILL.md").write_text("# no frontmatter\n", encoding="utf-8")
            audit = build_audit(discover_skills([Path(temp_dir)]))
            self.assertGreater(audit["summary"]["critical"], 0)

    def test_route_explicit_trigger(self):
        registry = {
            "entries": [
                {"name": "alpha", "status": "active", "path": "A", "issues": [], "is_system": False, "triggers": ["创建新 Skill"], "aliases": [], "priority": 10, "categories": []},
                {"name": "beta", "status": "active", "path": "B", "issues": [], "is_system": False, "triggers": ["other task"], "aliases": [], "priority": 0, "categories": []}
            ]
        }
        self.assertEqual("alpha", route(registry, "请帮我创建新 Skill")[0]["name"])


if __name__ == "__main__":
    unittest.main()