from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from msdmd.collect import collect, render_typescript


class CollectTest(unittest.TestCase):
    def test_collect_emits_declarations_gaps_and_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = root / "module.py"
            checks = root / "test_module.py"
            gap = root / "gap.py"
            module.write_text(
                """# === DEPENDENCIES ===
# id: module_edges
#   summary: module depends on another module
#   requires: other_module
# === END DEPENDENCIES ===

# === DOCS ===
# id: module_docs
#   summary: module docs
#   source: docs/module.md
#   status: current
# === END DOCS ===
""",
                encoding="utf-8",
            )
            checks.write_text(
                """# === CHECKS ===
# id: check_module_edges
#   proves: module_contract
#   call: self::test_module_edges
# === END CHECKS ===
""",
                encoding="utf-8",
            )
            gap.write_text("print('gap')\n", encoding="utf-8")

            collection = collect(
                root,
                "sample",
                block_names=("DEPENDENCIES", "DOCS", "CHECKS"),
                expected_blocks=("DOCS",),
                source_commit="abc123",
            )

            self.assertEqual("sample", collection["repo"])
            self.assertEqual("abc123", collection["source_commit"])
            self.assertEqual(
                [
                    {
                        "file": "module.py",
                        "block": "DEPENDENCIES",
                        "id": "module_edges",
                        "fields": {
                            "summary": "module depends on another module",
                            "requires": "other_module",
                        },
                    },
                    {
                        "file": "module.py",
                        "block": "DOCS",
                        "id": "module_docs",
                        "fields": {
                            "summary": "module docs",
                            "source": "docs/module.md",
                            "status": "current",
                        },
                    },
                    {
                        "file": "test_module.py",
                        "block": "CHECKS",
                        "id": "check_module_edges",
                        "fields": {
                            "proves": "module_contract",
                            "call": "self::test_module_edges",
                        },
                    },
                ],
                collection["declarations"],
            )
            self.assertEqual([{"file": "gap.py", "missing": ["DOCS"]}], collection["gaps"])
            self.assertEqual(
                [
                    {
                        "from": "check_module_edges",
                        "to": "self::test_module_edges",
                        "kind": "calls",
                        "source_block": "CHECKS",
                        "source_id": "check_module_edges",
                    },
                    {
                        "from": "check_module_edges",
                        "to": "module_contract",
                        "kind": "claims_proves",
                        "source_block": "CHECKS",
                        "source_id": "check_module_edges",
                    },
                    {
                        "from": "module_edges",
                        "to": "other_module",
                        "kind": "requires",
                        "source_block": "DEPENDENCIES",
                        "source_id": "module_edges",
                    },
                ],
                collection["edges"],
            )

    def test_render_typescript_uses_collection_helper(self) -> None:
        rendered = render_typescript(
            {"repo": "sample", "declarations": [], "gaps": [], "edges": []},
            import_path="./msdmd/collection",
        )

        self.assertIn('import { defineMsdmdCollection } from "./msdmd/collection";', rendered)
        self.assertIn("export default defineMsdmdCollection", rendered)
        self.assertIn('"repo": "sample"', rendered)


if __name__ == "__main__":
    unittest.main()
