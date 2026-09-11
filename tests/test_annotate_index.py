# ratios: loc_comments=149:1 imports_exports=6:1 calls_definitions=93:11
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
            '\"\"\"storage.\"\"\"\n\n'
            "def save():\n"
            "    return 1\n",
            encoding="utf-8",
        )
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
            self.assertEqual(routes["declared"], 2)
            self.assertEqual(routes["consumed"], 1)
            self.assertEqual(routes["fan_out"], 1)
            self.assertEqual(routes["fan_in"], 0)
            self.assertEqual(store["fan_in"], 1)
            self.assertEqual(store["fan_out"], 0)
            self.assertEqual(store["declared"], 0)

    def test_import_graph_exposes_the_same_relative_import_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            self._tree(td)
            files = A.collect_files(td)
            graph = A.build_import_graph(files)
            routes = str(td / "pkg" / "routes.py")
            store = str(td / "pkg" / "store.py")
            self.assertIn(store, graph["adjacency"][routes])
            self.assertEqual(graph["unresolved"], [])
            self.assertEqual(graph["ambiguous"], [])

    def test_named_seals_self_exclude_without_becoming_compact_seals(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            py_seal = "# ratios: loc_comments=2:1 imports_exports=0:1 calls_definitions=0:1"
            ts_seal = "// ratios: loc_comments=1:1 imports_exports=0:1 calls_definitions=0:0"
            py = td / "named.py"
            ts = td / "named.ts"
            py.write_text(
                py_seal + "\n\"\"\"doc.\"\"\"\ndef public():\n    return 1\n" + py_seal + "\n",
                encoding="utf-8",
            )
            ts.write_text(
                ts_seal + "\n// doc\nexport const value = 1;\n" + ts_seal + "\n",
                encoding="utf-8",
            )

            idx = A.build_index(A.collect_files(td), td)
            self.assertEqual((idx[str(py)]["code"], idx[str(py)]["comment"]), (2, 1))
            self.assertEqual((idx[str(ts)]["code"], idx[str(ts)]["comment"]), (1, 1))
            self.assertTrue(A._is_named_seal(py_seal))
            self.assertTrue(A._is_named_seal(ts_seal))
            self.assertFalse(A._is_seal(py_seal, ".py"))
            self.assertFalse(A._is_seal(ts_seal, ".ts"))

    def test_seal_line_format(self):
        m = {"code": 4, "comment": 1, "consumed": 1, "declared": 2,
             "fan_in": 0, "fan_out": 1}
        self.assertEqual(A.seal_line(m, "#"), "# 4:1 1:2 0:1")
        self.assertEqual(A.seal_line(m, "//"), "// 4:1 1:2 0:1")

    def test_pure_library_reads_zero_cd(self):
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
            self.assertEqual(A.main(["--root", str(td), "--check"]), 0)
            for f in A.collect_files(td):
                lines = f.read_text(encoding="utf-8").splitlines()
                self.assertTrue(A._is_seal(lines[0], f.suffix))
                self.assertTrue(A._is_seal(lines[-1], f.suffix))

    def test_write_and_check_preserve_python_and_node_shebangs(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            scripts = {
                td / "tool.py": "#!/usr/bin/env python3",
                td / "tool.ts": "#!/usr/bin/env node",
            }
            for path, shebang in scripts.items():
                path.write_text(shebang + "\nprint('ok')\n", encoding="utf-8")
            self.assertEqual(A.main(["--root", str(td), "--write"]), 0)
            self.assertEqual(A.main(["--root", str(td), "--check"]), 0)
            for path, shebang in scripts.items():
                with self.subTest(path=path):
                    lines = path.read_text(encoding="utf-8").splitlines()
                    self.assertEqual(shebang, lines[0])
                    self.assertTrue(A._is_seal(lines[1], path.suffix))
                    self.assertEqual(lines[1], lines[-1])

    def test_write_repairs_a_seal_that_displaced_the_shebang(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            script = td / "tool.py"
            shebang = "#!/usr/bin/env python3"
            script.write_text(shebang + "\nprint('ok')\n", encoding="utf-8")
            self.assertEqual(A.main(["--root", str(td), "--write"]), 0)
            lines = script.read_text(encoding="utf-8").splitlines()
            script.write_text(
                "\n".join([lines[1], lines[0], *lines[2:]]) + "\n",
                encoding="utf-8",
            )
            self.assertEqual(A.main(["--root", str(td), "--check"]), 1)
            self.assertEqual(A.main(["--root", str(td), "--write"]), 0)
            lines = script.read_text(encoding="utf-8").splitlines()
            self.assertEqual(shebang, lines[0])
            self.assertTrue(A._is_seal(lines[1], ".py"))
            self.assertEqual(lines[1], lines[-1])

    def test_check_rejects_a_stale_closing_seal(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            script = td / "tool.py"
            script.write_text("print('ok')\n", encoding="utf-8")
            self.assertEqual(A.main(["--root", str(td), "--write"]), 0)
            lines = script.read_text(encoding="utf-8").splitlines()
            lines[-1] = "# 9:9 9:9 9:9"
            script.write_text("\n".join(lines) + "\n", encoding="utf-8")
            self.assertEqual(A.main(["--root", str(td), "--check"]), 1)


if __name__ == "__main__":
    unittest.main()
# ratios: loc_comments=149:1 imports_exports=6:1 calls_definitions=93:11
