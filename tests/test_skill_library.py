from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_JSON = ROOT / "skills.json"
RATIO_BOOKEND_RE = re.compile(r"^(?P<marker>#|//|--) (?P<ratios>\d+:\d+ \d+:\d+ \d+:\d+)$")


class SkillLibraryTest(unittest.TestCase):
    def test_skills_json_matches_skill_directories(self) -> None:
        data = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
        registered_paths = {skill["path"] for skill in data["skills"]}
        actual_paths = {str(path.relative_to(ROOT)) for path in ROOT.glob("*/SKILL.md")}

        self.assertEqual(actual_paths, registered_paths)
        for skill in data["skills"]:
            self.assertIn("name", skill)
            self.assertIn("description", skill)
            self.assertTrue((ROOT / skill["path"]).exists(), skill["path"])

    def test_skill_frontmatter_has_name_and_description(self) -> None:
        for path in sorted(ROOT.glob("*/SKILL.md")):
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            _, frontmatter, _ = text.split("---\n", 2)
            keys = {
                line.split(":", 1)[0].strip()
                for line in frontmatter.splitlines()
                if ":" in line
            }
            self.assertIn("name", keys, path)
            self.assertIn("description", keys, path)

    def test_readme_lists_every_skill(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        data = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
        for skill in data["skills"]:
            self.assertIn(f"[`{skill['name']}/`]({skill['path']})", readme)

    def test_parser_ratio_bookends_are_single_matching_lines(self) -> None:
        parser_files = sorted((ROOT / "msdmd" / "parsers").glob("*"))
        parser_files = [path for path in parser_files if path.is_file()]
        self.assertGreater(parser_files, [])

        for path in parser_files:
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(lines), 2, path)
            first = lines[0]
            last = lines[-1]
            self.assertEqual(first, last, path)

            match = RATIO_BOOKEND_RE.fullmatch(first)
            self.assertIsNotNone(match, f"{path}: {first!r}")
            self.assertRegex(match.group("ratios"), r"^\d+:\d+ \d+:\d+ \d+:\d+$")

            interior_bookends = [
                line for line in lines[1:-1] if RATIO_BOOKEND_RE.fullmatch(line)
            ]
            self.assertEqual([], interior_bookends, path)


if __name__ == "__main__":
    unittest.main()
