# ratios: loc_comments=86:0 imports_exports=6:1 calls_definitions=39:7
import math
from pathlib import Path
import sys
import tempfile
import unittest

RATIOS = Path(__file__).resolve().parents[1] / 'ratios'
sys.path.insert(0, str(RATIOS))
import harmonics as H


class HarmonicsTest(unittest.TestCase):
    def test_cycle_graph_groups_degenerate_modes(self):
        graph = {
            'a': {'b', 'd'},
            'b': {'a', 'c'},
            'c': {'b', 'd'},
            'd': {'a', 'c'},
        }
        signal = {'a': 1.0, 'b': 0.0, 'c': -1.0, 'd': 0.0}
        report = H.graph_harmonics(graph, signal, permutations=0)
        modes = report['modes']
        self.assertTrue(any(m['multiplicity'] == 2 and abs(m['eigenvalue'] - 2.0) < 1e-7 for m in modes))
        dominant = max(modes, key=lambda m: m['energy_fraction'])
        self.assertEqual(dominant['multiplicity'], 2)
        self.assertAlmostEqual(dominant['energy_fraction'], 1.0, places=7)

    def test_harmonic_scan_finds_two_cycles(self):
        x = [i / 39 for i in range(40)]
        y = [math.sin(4.0 * math.pi * value) for value in x]
        modes = H.harmonic_scan(x, y, max_harmonic=6, permutations=0)
        dominant = max(modes, key=lambda m: m['power'])
        self.assertEqual(dominant['harmonic'], 2)
        self.assertGreater(dominant['power'], 0.99)

    def test_contrast_preserves_zero_zero_as_undefined(self):
        self.assertIsNone(H.bounded_contrast(0, 0))
        self.assertEqual(H.bounded_contrast(3, 1), 0.5)

    def test_semantic_graph_projects_ids_to_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = str((root / 'a.py').resolve())
            b = str((root / 'b.py').resolve())
            collection = {
                'declarations': [
                    {'file': 'a.py', 'id': 'alpha'},
                    {'file': 'b.py', 'id': 'beta'},
                ],
                'edges': [
                    {'source_id': 'alpha', 'to': 'beta'},
                    {'source_id': 'alpha', 'to': 'missing'},
                ],
            }
            report = H.semantic_file_graph(collection, root, [a, b])
            self.assertEqual(report['adjacency'][a], [b])
            self.assertEqual(report['resolved_edges'], 1)
            self.assertEqual(report['unresolved_edges'], ['alpha->missing'])

    def test_source_balance_excludes_ratio_seals(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'sample.py'
            path.write_text(
                '# ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:0\n'
                '# comment\n'
                'x = 1\n'
                '# ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:0\n',
                encoding='utf-8',
            )
            x, y, counts = H.source_balance_series(path)
            self.assertEqual(y, [-1.0, 1.0])
            self.assertEqual(counts['code'], 1)
            self.assertEqual(counts['comment'], 1)
            self.assertEqual(x, [0.0, 1.0])

    def test_import_domain_runs_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pkg").mkdir()
            modules = {
                "a.py": "from .b import value\na = 1\n",
                "b.py": "from .c import value\nb = 1\nb2 = 2\n",
                "c.py": "from .d import value\nc = 1\nc2 = 2\nc3 = 3\n",
                "d.py": "from .a import value\nd = 1\n",
            }
            for name, body in modules.items():
                (root / "pkg" / name).write_text(body, encoding="utf-8")
            rc = H.main([
                "--root", str(root), "--domain", "import", "--signal", "code",
                "--permutations", "0", "--max-nodes", "16", "--top", "2",
            ])
            self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
# ratios: loc_comments=86:0 imports_exports=6:1 calls_definitions=39:7
