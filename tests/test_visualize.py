from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from msdmd.collect import render_typescript
from msdmd.visualize import _node_id, load_collection, render_mermaid


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

    def test_load_collection_reads_generated_schema_two_with_legacy_name_in_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample_msdmd.ts"
            collection = {
                "schema_version": "2.0.0",
                "repo": "sample",
                "declarations": [],
                "facts": [{"note": "defineMsdmdCollection({not the wrapper})"}],
                "gaps": [],
                "edges": [],
            }
            path.write_text(
                render_typescript(collection, import_path="./msdmd/collection"),
                encoding="utf-8",
            )

            loaded = load_collection(path)

        self.assertEqual("2.0.0", loaded["schema_version"])
        self.assertEqual(collection["facts"], loaded["facts"])

    def test_load_collection_reads_hand_authored_typescript(self) -> None:
        hand_authored = (
            "// ratios: loc_comments=10:2 imports_exports=1:0 calls_definitions=1:0\n"
            'import { defineMsdmdCollection } from "./msdmd/collection";\n'
            "\n"
            "// Hand-curated collection point (unquoted keys, trailing commas).\n"
            "export default defineMsdmdCollection({\n"
            '  repo: "sample",\n'
            "  declarations: [\n"
            "    {\n"
            '      file: "module.py", // trailing comment with ) and " inside\n'
            '      block: "DEPENDENCIES",\n'
            "      id: 'module_edges',\n"
            '      fields: { requires: "other_module", },\n'
            "    },\n"
            "  ],\n"
            '  gaps: [{ file: "gap.py", missing: ["DOCS"], }],\n'
            "  edges: [\n"
            "    {\n"
            '      from: "module_edges",\n'
            '      to: "other_module",\n'
            '      kind: "requires",\n'
            '      source_block: "DEPENDENCIES",\n'
            '      source_id: "module_edges",\n'
            "    },\n"
            "  ],\n"
            "});\n"
            "// ratios: loc_comments=10:2 imports_exports=1:0 calls_definitions=1:0\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample_msdmd.ts"
            path.write_text(hand_authored, encoding="utf-8")
            collection = load_collection(path)

        self.assertEqual("sample", collection["repo"])
        self.assertEqual(self.sample_collection(), collection)

    def test_load_collection_reads_repo_collection_point(self) -> None:
        path = Path(__file__).resolve().parent.parent / "skill-lib_msdmd.ts"
        collection = load_collection(path)

        self.assertEqual("The-Interdependency/skill-lib", collection["repo"])
        self.assertTrue(collection["declarations"])
        self.assertTrue(collection["edges"])
        self.assertTrue(collection["gaps"])
        self.assertIn("flowchart TD", render_mermaid(collection))

    def test_load_collection_rejects_non_collection_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "other.ts"
            path.write_text("export const x = 1;\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_collection(path)

    def test_render_mermaid_contains_repo_edges_and_gaps(self) -> None:
        rendered = render_mermaid(self.sample_collection())

        self.assertIn("flowchart TD", rendered)
        self.assertIn(f'{_node_id("repository:sample")}["sample"]', rendered)
        self.assertIn('["module_edges\\nDEPENDENCIES\\nmodule.py"]', rendered)
        self.assertIn('-- "requires" -->', rendered)
        self.assertIn('gap_1[["gap.py\\nmissing: DOCS"]]', rendered)

    def test_render_mermaid_keeps_same_entry_id_in_two_files_distinct(self) -> None:
        collection = {
            "schema_version": "2.0.0",
            "repo": "sample",
            "declarations": [
                {"address": "msdmd://sample@abc/a.py#block/DOCS/shared", "file": "a.py", "block": "DOCS", "id": "shared", "fields": {}},
                {"address": "msdmd://sample@abc/b.py#block/DOCS/shared", "file": "b.py", "block": "DOCS", "id": "shared", "fields": {}},
            ],
            "facts": [],
            "gaps": [],
            "edges": [],
            "diagnostics": [],
        }

        rendered = render_mermaid(collection)

        self.assertIn(_node_id(collection["declarations"][0]["address"]), rendered)
        self.assertIn(_node_id(collection["declarations"][1]["address"]), rendered)
        self.assertNotEqual(_node_id(collection["declarations"][0]["address"]), _node_id(collection["declarations"][1]["address"]))


if __name__ == "__main__":
    unittest.main()
