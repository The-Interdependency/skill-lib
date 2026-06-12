from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from frontmatter import frontmatter_for


class FrontmatterParserTest(unittest.TestCase):
    def parse(self, body: str) -> dict[str, str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(f"---\n{body}---\n# Body\n", encoding="utf-8")
            return frontmatter_for(path)

    def test_parses_folded_description(self) -> None:
        frontmatter = self.parse(
            "name: manifest\n"
            "description: >-\n"
            "  Living-spec generator.\n"
            "  Load this when maintaining generated repo facts.\n"
        )

        self.assertEqual("manifest", frontmatter["name"])
        self.assertEqual(
            "Living-spec generator. Load this when maintaining generated repo facts.",
            frontmatter["description"],
        )

    def test_parses_literal_description(self) -> None:
        frontmatter = self.parse(
            "name: manifest\n"
            "description: |-\n"
            "  line one\n"
            "  line two\n"
        )

        self.assertEqual("line one\nline two", frontmatter["description"])


if __name__ == "__main__":
    unittest.main()
