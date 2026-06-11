from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from msdmd.collect import render_typescript
from msdmd.visualize import load_collection, render_mermaid


class VisualizeTest(unittest.TestCase):
    def sample_collection(self) -> dict:
        return {
            "repo": "sample",
            "declarations": [
                {
                    "file": "module.py",
                    "block": "DEPENDENCIES",
                    "id": "module_edges",
                    "fields": {"requires": "other_module"},
                }
            ],
            "gaps": [{"file": "gap.py", "missing": ["DOCS"]}],
            "edges": [
                {
                    "from": "module_edges",
                    "to": "other_module",
                    "kind": "requires",
                    "source_block": "DEPENDENCIES",
                    "source_id": "module_edges",
                }
            ],
        }

    def test_load_collection_reads_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "collection.json"
            path.write_text(json.dumps(self.sample_collection()), encoding="utf-8")
            self.assertEqual("sample", load_collection(path)["repo"])

    def test_load_collection_reads_generated_typescript(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample_msdmd.ts"
            path.write_text(
                render_typescript(self.sample_collection(), import_path="./msdmd/collection"),
                encoding="utf-8",
            )
            self.assertEqual("sample", load_collection(path)["repo"])

    def test_render_mermaid_contains_repo_edges_and_gaps(self) -> None:
        rendered = render_mermaid(self.sample_collection())

        self.assertIn("flowchart TD", rendered)
        self.assertIn('repo["sample"]', rendered)
        self.assertIn('module_edges["module_edges\\nDEPENDENCIES\\nmodule.py"]', rendered)
        self.assertIn('module_edges -- "requires" --> other_module', rendered)
        self.assertIn('gap_1[["gap.py\\nmissing: DOCS"]]', rendered)


if __name__ == "__main__":
    unittest.main()
