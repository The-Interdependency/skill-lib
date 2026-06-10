from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION_TS = ROOT / "msdmd" / "collection.ts"
EXPECTED_BLOCKS = {
    "DOCS",
    "CAPABILITIES",
    "DEPENDENCIES",
    "OWNERS",
    "CONTRACTS",
    "MODULE_BUILD",
    "BOUNDARIES",
    "RATIOS",
}


class CollectionSchemaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.source = COLLECTION_TS.read_text(encoding="utf-8")

    def test_collection_schema_exports_required_types(self) -> None:
        for exported in [
            "MsdmdBlockName",
            "MsdmdFieldMap",
            "MsdmdDeclaration",
            "MsdmdGap",
            "MsdmdEdge",
            "MsdmdCollection",
            "defineMsdmdCollection",
        ]:
            with self.subTest(exported=exported):
                self.assertIn(f"export ", self.source)
                self.assertIn(exported, self.source)

    def test_block_name_union_covers_registered_application_blocks(self) -> None:
        declared_blocks = set(re.findall(r'\| "([A-Z_]+)"', self.source))
        self.assertEqual(EXPECTED_BLOCKS, declared_blocks)

    def test_declaration_gap_and_edge_shapes_have_visualizer_fields(self) -> None:
        for field in [
            "file: string",
            "block: MsdmdBlockName",
            "id: string",
            "fields: MsdmdFieldMap",
            "missing: MsdmdBlockName[]",
            "from: string",
            "to: string",
            "kind: string",
            "source_block: MsdmdBlockName",
            "source_id: string",
            "edges?: MsdmdEdge[]",
        ]:
            with self.subTest(field=field):
                self.assertIn(field, self.source)


if __name__ == "__main__":
    unittest.main()
