# ratios: loc_comments=121:28 imports_exports=5:1 calls_definitions=23:4
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from msdmd.collect import SCHEMA_VERSION, collect, collect_legacy, render_typescript


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
            self.assertEqual(SCHEMA_VERSION, collection["schema_version"])
            self.assertEqual("abc123", collection["source"]["revision"])
            self.assertEqual(
                [
                    ("module.py", "DEPENDENCIES", "module_edges"),
                    ("module.py", "DOCS", "module_docs"),
                    ("test_module.py", "CHECKS", "check_module_edges"),
                ],
                [(item["file"], item["block"], item["id"]) for item in collection["declarations"]],
            )
            self.assertTrue(all(item["address"].startswith("msdmd://sample@abc123/") for item in collection["declarations"]))
            self.assertEqual(
                [
                    {"file": "gap.py", "missing": ["DOCS"], "kind": "block-adoption"},
                    {"file": "test_module.py", "missing": ["DOCS"], "kind": "block-adoption"},
                ],
                collection["gaps"],
            )
            block_edges = [item for item in collection["edges"] if "source_block" in item]
            self.assertEqual(["calls", "claims_proves", "requires"], sorted(item["kind"] for item in block_edges))
            self.assertTrue(all(item["from"].startswith("msdmd://sample@abc123/") for item in block_edges))
            self.assertTrue(all(item["source_id"] == item["from"] for item in block_edges))

    def test_render_typescript_uses_collection_helper(self) -> None:
        rendered = render_typescript(
            {"schema_version": SCHEMA_VERSION, "repo": "sample", "declarations": [], "gaps": [], "edges": []},
            import_path="./msdmd/collection",
        )

        self.assertIn('import { defineMsdmdCollectionV2 } from "./msdmd/collection";', rendered)
        self.assertIn("export default defineMsdmdCollectionV2", rendered)
        self.assertIn('"repo": "sample"', rendered)

    def test_collect_legacy_is_explicitly_block_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "module.py").write_text(
                "# === DOCS ===\n# id: module_docs\n#   summary: docs\n# === END DOCS ===\n",
                encoding="utf-8",
            )
            collection = collect_legacy(root, "sample", block_names=("DOCS",), source_commit="abc123")

        self.assertEqual("1.0.0", collection["schema_version"])
        self.assertNotIn("facts", collection)
        self.assertEqual("abc123", collection["source_commit"])

    def test_collect_skips_vendored_agent_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            product = root / "product.py"
            vendored = root / ".agents" / "skills" / "msdmd" / "ignored.py"
            vendored.parent.mkdir(parents=True)

            product.write_text(
                """# === DOCS ===
# id: product_doc
#   path: docs/product.md
# === END DOCS ===
""",
                encoding="utf-8",
            )
            vendored.write_text(
                """# === DOCS ===
# id: vendored_doc
#   path: docs/ignored.md
# === END DOCS ===
""",
                encoding="utf-8",
            )

            collection = collect(root, "sample", block_names=("DOCS",))

            self.assertEqual(
                [("product.py", "product_doc")],
                [(item["file"], item["id"]) for item in collection["declarations"]],
            )


if __name__ == "__main__":
    unittest.main()
# ratios: loc_comments=121:28 imports_exports=5:1 calls_definitions=23:4
