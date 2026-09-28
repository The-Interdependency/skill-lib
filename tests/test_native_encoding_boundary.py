"""Malformed-source regression: python -m unittest tests.test_native_encoding_boundary."""
from pathlib import Path
import tempfile
import unittest

from msdmd.collect import collect, collection_errors


class NativeEncodingBoundaryTests(unittest.TestCase):
    def test_malformed_code_with_ratios_preserves_other_files_and_reports_error(self):
        for suffix in ('.ts', '.rs', '.java', '.cpp', '.h'):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                name = 'broken' + suffix
                (root / name).write_bytes(b'// ratios: loc_comments=1:1 imports_exports=0:0 calls_definitions=0:0\n\xff')
                (root / 'healthy.json').write_text('{"name":"preserved"}')
                result = collect(root, 'fixture', source_commit='a' * 40)
                self.assertTrue(collection_errors(result))
                self.assertTrue(any(d['code'] == 'native_reader_error' and d['source']['file'] == name for d in result['diagnostics']))
                self.assertEqual('invalid', next(d['status'] for d in result['discovery'] if d['file'] == name))
                self.assertTrue(any(f['source']['file'] == 'healthy.json' and f['native']['value'].get('name') == 'preserved' for f in result['facts']))
