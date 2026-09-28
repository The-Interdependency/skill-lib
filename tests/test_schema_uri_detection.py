"""URI recognition regressions: python -m unittest tests.test_schema_uri_detection."""
import json
from pathlib import Path
import tempfile
import unittest

from msdmd.collect import collect, collection_errors
from msdmd.formats import is_json_schema_uri


class SchemaUriDetectionTests(unittest.TestCase):
    def collection(self, schema, **options):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'sample.json').write_text(json.dumps({'$schema': schema, 'x-custom': [1, True]}))
            return collect(root, 'fixture', source_commit='a' * 40, **options)

    def test_exact_authority_and_canonical_drafts(self):
        for uri in ('http://json-schema.org/draft-04/schema#',
                    'https://json-schema.org/draft/2020-12/schema',
                    'https://JSON-SCHEMA.ORG/draft/2020-12/schema'):
            with self.subTest(uri=uri):
                self.assertTrue(is_json_schema_uri(uri))

    def test_host_lookalikes_userinfo_controls_and_nonstrings_rejected(self):
        for uri in ('https://json-schema.org.attacker.invalid/schema',
                    'https://attacker.invalid/json-schema.org/schema',
                    'https://attacker.invalid/?next=https://json-schema.org/schema',
                    'https://json-schema.org@attacker.invalid/schema',
                    'https://user@json-schema.org/schema',
                    'https://json-schema.org:443/schema',
                    '//json-schema.org/schema', 'ftp://json-schema.org/schema',
                    ' https://json-schema.org/schema',
                    'https://json-schema.org/\nschema', 'https://[invalid/schema',
                    None, True, 42, ['https://json-schema.org/schema'],
                    {'uri': 'https://json-schema.org/schema'}):
            with self.subTest(uri=uri):
                self.assertFalse(is_json_schema_uri(uri))

    def test_collection_preserves_lookalikes_without_schema_classification(self):
        for uri in ('https://attacker.invalid/json-schema.org/schema',
                    'https://json-schema.org.attacker.invalid/schema',
                    ['https://json-schema.org/draft/2020-12/schema']):
            with self.subTest(uri=uri):
                result = self.collection(uri)
                self.assertFalse(collection_errors(result))
                self.assertFalse(any(f['convention']['namespace'] == 'json.schema' for f in result['facts']))
                docs = [f for f in result['facts'] if f['kind'] == 'structured-document']
                self.assertTrue(any(f['native']['value']['$schema'] == uri for f in docs))

    def test_supported_draft_and_unknown_fields_still_collected(self):
        result = self.collection('https://json-schema.org/draft/2020-12/schema')
        self.assertFalse(collection_errors(result))
        schemas = [f for f in result['facts'] if f['kind'] == 'schema-description']
        self.assertEqual(1, len(schemas))
        self.assertEqual([1, True], schemas[0]['native']['value']['x-custom'])

    def test_unknown_canonical_draft_is_unresolved_required_scope(self):
        result = self.collection('https://json-schema.org/draft/future/schema', required_sources=['sample.json'])
        self.assertTrue(collection_errors(result))
        self.assertIn('unsupported_json_schema_draft', {d['code'] for d in result['diagnostics']})
