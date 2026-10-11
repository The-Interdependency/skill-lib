"""Consumer P1 regressions. Usage: python -m unittest tests.test_native_p1_security."""
from __future__ import annotations

import base64
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from msdmd.collect import collect, collection_errors


class NativeP1SecurityTests(unittest.TestCase):
    def collection(self, name, content):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / name).write_text(content, encoding='utf-8')
            return collect(root, 'fixture', source_commit='a' * 40)

    def test_yaml_toml_unsafe_integers_preserve_exact_values_in_javascript(self):
        for name, source in [('sample.yaml', 'large: 9223372036854775807\nnegative: -9007199254740993\nsafe: 9007199254740991\nboolean: true\n'),
                             ('sample.toml', 'large = 9223372036854775807\nnegative = -9007199254740993\nsafe = 9007199254740991\nboolean = true\n')]:
            with self.subTest(name=name):
                result = self.collection(name, source)
                self.assertFalse(collection_errors(result), result['diagnostics'])
                value = next(f['native']['value'] for f in result['facts'] if f['kind'] == 'structured-document')
                self.assertEqual({'$type': 'json-number', 'lexeme': '9223372036854775807'}, value['large'])
                self.assertEqual('-9007199254740993', value['negative']['lexeme'])
                self.assertEqual(9007199254740991, value['safe'])
                self.assertIs(True, value['boolean'])
                wire = subprocess.run(['node', '-e', 'process.stdout.write(JSON.stringify(JSON.parse(require("node:fs").readFileSync(0,"utf8"))))'],
                    input=json.dumps(value), text=True, capture_output=True, check=True).stdout
                self.assertEqual(value, json.loads(wire))

    def test_mixed_yaml_mapping_redacts_values_without_losing_typed_keys(self):
        result = self.collection('mixed.yaml', 'password: DO_NOT_PUBLISH_mixed\n1: harmless\nnested:\n  2: public\n  apiToken: DO_NOT_PUBLISH_nested\n')
        self.assertFalse(collection_errors(result), result['diagnostics'])
        self.assertNotIn('DO_NOT_PUBLISH', json.dumps(result))
        value = next(f['native']['value'] for f in result['facts'] if f['kind'] == 'structured-document')
        self.assertEqual('yaml-mapping', value['$type'])
        self.assertEqual(1, value['entries'][1]['key'])
        self.assertEqual('harmless', value['entries'][1]['value'])
        self.assertTrue(value['entries'][0]['value']['$redacted'])
        self.assertIn('sensitive_fields_redacted', json.dumps(result))

    def test_kubernetes_secret_containers_are_withheld_in_lists_and_typed_maps(self):
        for source in ['apiVersion: v1\nkind: Secret\nmetadata:\n  name: cert\ndata:\n  tls.key: DO_NOT_PUBLISH_encoded\nstringData:\n  config.json: DO_NOT_PUBLISH_plain\n',
                       'kind: List\nitems:\n  - kind: Secret\n    data:\n      arbitrary: DO_NOT_PUBLISH_nested\n',
                       'kind: Secret\n1: public\ndata:\n  arbitrary: DO_NOT_PUBLISH_mixed\n']:
            with self.subTest(source=source):
                result = self.collection('resource.yaml', source)
                self.assertFalse(collection_errors(result), result['diagnostics'])
                self.assertNotIn('DO_NOT_PUBLISH', json.dumps(result))
                self.assertIn('sensitive_fields_redacted', json.dumps(result))
        ordinary = self.collection('resource.yaml', 'kind: ConfigMap\ndata:\n  config.json: public\n')
        self.assertIn('public', json.dumps(ordinary))

    def test_credential_identifiers_are_sanitized_before_addresses(self):
        url = 'https://user:DO_NOT_PUBLISH_native@example.com/schema'
        fixtures = [('schema.json', {'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': url}),
                    ('sbom.json', {'bomFormat': 'CycloneDX', 'specVersion': '1.6', 'components': [{'bom-ref': url}]}),
                    ('api.json', {'openapi': '3.1.0', 'paths': {url: {'get': {'operationId': url}}}})]
        for name, source in fixtures:
            with self.subTest(name=name):
                result = self.collection(name, json.dumps(source))
                self.assertFalse(collection_errors(result), result['diagnostics'])
                self.assertNotIn('DO_NOT_PUBLISH', json.dumps(result))
                self.assertIn('redacted', json.dumps(result))

    def test_malformed_dsse_subject_keeps_redacted_decoded_evidence(self):
        for subjects in [[None, 1, 'invalid', {'name': 'valid'}], None, {'name': 'wrong-container'}]:
            with self.subTest(subjects=subjects):
                statement = {'_type': 'https://in-toto.io/Statement/v1', 'subject': subjects, 'predicate': {'password': 'DO_NOT_PUBLISH_dsse'}}
                payload = base64.b64encode(json.dumps(statement).encode()).decode()
                result = self.collection('attestation.json', json.dumps({'payloadType': 'application/vnd.in-toto+json', 'payload': payload}))
                self.assertNotIn(payload, json.dumps(result))
                self.assertNotIn('DO_NOT_PUBLISH', json.dumps(result))
                self.assertTrue(any(f['kind'] == 'attestation' for f in result['facts']))
                self.assertIn('invalid_statement_subject', {d['code'] for d in result['diagnostics']})

    def test_raw_dsse_payload_is_withheld_even_if_semantic_reader_aborts(self):
        payload = base64.b64encode(b'{"password":"DO_NOT_PUBLISH_failure"}').decode()
        with patch('msdmd.readers.read_standards', side_effect=ValueError('failure')):
            result = self.collection('attestation.json', json.dumps({'payloadType': 'application/vnd.in-toto+json', 'payload': payload}))
        self.assertNotIn(payload, json.dumps(result))
        self.assertNotIn('DO_NOT_PUBLISH', json.dumps(result))
        self.assertTrue(collection_errors(result))
