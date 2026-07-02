# ratios: loc_comments=71:9 imports_exports=6:1 calls_definitions=40:6
"""Tests for the portable canonical-seal computer (ratios/annotate_index.py)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

RATIOS = Path(__file__).resolve().parents[1] / "ratios"
sys.path.insert(0, str(RATIOS))

import annotate_index as A  # noqa: E402


class BuildIndexTest(unittest.TestCase):
    def _tree(self, td: Path) -> None:
        # a route module declaring two DOC endpoints; imports a sibling.
        (td / "pkg").mkdir()
        (td / "pkg" / "__init__.py").write_text("", encoding="utf-8")
        (td / "pkg" / "routes.py").write_text(
            "# DOC endpoint: GET /health\n"
            "# DOC endpoint: POST /widgets\n"
            "from .store import save\n\n"
            "def handler():\n"
            "    return save()\n",
            encoding="utf-8",
        )
        (td / "pkg" / "store.py").write_text(
            '"""storage."""\n\n'
            "def save():\n"
            "    return 1\n",
            encoding="utf-8",
        )
        # a consumer dir referencing one of the declared endpoints
        (td / "client" / "src").mkdir(parents=True)
        (td / "client" / "src" / "api.ts").write_text(
            "export const url = '/health';\n", encoding="utf-8"
        )

    def test_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            self._tree(td)
            files = A.collect_files(td)
            idx = A.build_index(files, td)
            routes = idx[str(td / "pkg" / "routes.py")]
            store = idx[str(td / "pkg" / "store.py")]

            # routes.py: declares 2 endpoints; 1 (/health) consumed in client/src.
            self.assertEqual(routes["declared"], 2)
            self.assertEqual(routes["consumed"], 1)
            # routes.py imports store (relative) -> fan_out 1; nobody imports routes.
            self.assertEqual(routes["fan_out"], 1)
            self.assertEqual(routes["fan_in"], 0)
            # store.py: imported by routes via `from .store` -> fan_in 1.
            self.assertEqual(store["fan_in"], 1)
            self.assertEqual(store["fan_out"], 0)
            self.assertEqual(store["declared"], 0)  # no DOC endpoints -> 0:0

    def test_seal_line_format(self):
        m = {"code": 4, "comment": 1, "consumed": 1, "declared": 2,
             "fan_in": 0, "fan_out": 1}
        self.assertEqual(A.seal_line(m, "#"), "# 4:1 1:2 0:1")
        self.assertEqual(A.seal_line(m, "//"), "// 4:1 1:2 0:1")

    def test_pure_library_reads_zero_cd(self):
        # A library file with no routes and no importers -> C:D 0:0.
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            (td / "lib.py").write_text(
                "def public():\n    return 1\n", encoding="utf-8"
            )
            idx = A.build_index(A.collect_files(td), td)
            m = idx[str(td / "lib.py")]
            self.assertEqual((m["consumed"], m["declared"]), (0, 0))

    def test_write_and_check_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            self._tree(td)
            self.assertEqual(A.main(["--root", str(td), "--write"]), 0)
            # after stamping, --check must report no drift
            self.assertEqual(A.main(["--root", str(td), "--check"]), 0)
            # every file now opens and closes with a seal line
            for f in A.collect_files(td):
                lines = f.read_text(encoding="utf-8").splitlines()
                self.assertTrue(A._is_seal(lines[0], f.suffix))
                self.assertTrue(A._is_seal(lines[-1], f.suffix))


if __name__ == "__main__":
    unittest.main()
# ratios: loc_comments=71:9 imports_exports=6:1 calls_definitions=40:6
