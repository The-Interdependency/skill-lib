"""Reviewed regressions: python -m unittest tests.test_native_review_regressions."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from msdmd.collect import collect, collection_errors
from msdmd.formats import parse_json, parse_yaml


class NativeReviewRegressions(unittest.TestCase):
    def collection(self, files, **options):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name, content in files.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content if isinstance(content, bytes) else content.encode())
            return collect(root, 'fixture', source_commit='a' * 40, **options)

    def facts(self, result, namespace=None, kind=None):
        return [f for f in result['facts'] if (namespace is None or f['convention']['namespace'] == namespace)
                and (kind is None or f['kind'] == kind)]

    def test_missing_comment_parser_retains_uncertified_candidates_and_fails_closed(self):
        source = '// === DOCS ===\n// id: rescued\n//   owner: team\n// === END DOCS ===\nexport const x = 1;\n'
        with patch('msdmd.native_code.run_node', side_effect=FileNotFoundError()):
            result = self.collection({'a.ts': source})
        self.assertTrue(collection_errors(result))
        candidates = [d for d in result['diagnostics'] if d['code'] == 'supplemental_comment_extraction_unavailable']
        self.assertTrue(candidates)
        self.assertIn('rescued', json.dumps(candidates))
        self.assertFalse(result['declarations'])

    def test_ambiguous_header_block_candidates_are_not_silent_success(self):
        source = '// === DOCS ===\n// id: header_candidate\n// === END DOCS ===\nint x;\n'
        result = self.collection({'a.h': source})
        self.assertTrue(collection_errors(result))
        self.assertIn('header_candidate', json.dumps(result['diagnostics']))
        self.assertFalse(result['declarations'])

    def test_systemd_continuations_preserve_separators_and_skip_comments(self):
        source = '[Service]\nExecStart=/bin/echo one' + chr(92) + '\n# skipped\n; skipped too\n  two\n'
        result = self.collection({'a.service': source})
        self.assertFalse(collection_errors(result))
        directive = self.facts(result, 'systemd.unit', 'unit-directive')[0]
        self.assertEqual('/bin/echo one two', directive['native']['value']['value'])
        self.assertEqual(2, directive['source']['location']['start_line'])
        self.assertEqual(5, directive['source']['location']['end_line'])

    def test_every_systemd_environment_assignment_is_redacted(self):
        for value in ('A=1 API_TOKEN=DO_NOT_PUBLISH_a18 PASSWORD=DO_NOT_PUBLISH_b19 SAFE=ok',
                      '"A=a b" "API_TOKEN=DO_NOT_PUBLISH_c20 extra" SAFE=ok'):
            with self.subTest(value=value):
                result = self.collection({'a.service': '[Service]\nEnvironment = ' + value + '\n'})
                self.assertFalse(collection_errors(result))
                published = json.dumps(result)
                self.assertNotIn('DO_NOT_PUBLISH', published)
                self.assertIn('SAFE=ok', published)
                self.assertIn('sensitive_fields_redacted', published)

    def test_unimplemented_environment_escaping_is_withheld_and_partial(self):
        source = '[Service]\nEnvironment=A=1 API' + chr(92) + 'x5fTOKEN=DO_NOT_PUBLISH_d21\n'
        result = self.collection({'a.service': source}, required_sources=['a.service'])
        self.assertTrue(collection_errors(result))
        self.assertNotIn('DO_NOT_PUBLISH', json.dumps(result))
        self.assertIn('unsupported_systemd_environment_syntax', {d['code'] for d in result['diagnostics']})

    def test_requirement_includes_do_not_satisfy_required_source_policy(self):
        for directive in ('-r prod.txt', '-c constraints.txt', '--requirement=prod.txt', '--constraint constraints.txt', '-rprod.txt'):
            with self.subTest(directive=directive):
                result = self.collection({'requirements.txt': directive + '\n'}, required_sources=['requirements.txt'])
                self.assertTrue(collection_errors(result))
                self.assertIn('unresolved_requirement_include', {d['code'] for d in result['diagnostics']})
                self.assertEqual('partial', next(d['status'] for d in result['discovery'] if d['file'] == 'requirements.txt'))
                self.assertTrue(self.facts(result, kind='requirements-option'))

    def test_json_numeric_lexemes_survive_javascript_projection(self):
        value = parse_json(b'{"large":9007199254740993,"fraction":0.12345678901234567890,"negative_zero":-0,"safe":42,"half":1.5}')
        self.assertEqual({'$type': 'json-number', 'lexeme': '9007199254740993'}, value['large'])
        self.assertEqual('0.12345678901234567890', value['fraction']['lexeme'])
        self.assertEqual('-0', value['negative_zero']['lexeme'])
        self.assertEqual(42, value['safe'])
        self.assertEqual(1.5, value['half'])
        wire = subprocess.run(['node', '-e', 'process.stdout.write(JSON.stringify(JSON.parse(require("node:fs").readFileSync(0,"utf8"))))'],
            input=json.dumps(value), text=True, capture_output=True, check=True).stdout
        self.assertEqual(value, json.loads(wire))
        result = self.collection({'data.json': '{"large":9007199254740993}'})
        self.assertFalse(collection_errors(result))
        self.assertEqual('9007199254740993', self.facts(result, kind='structured-document')[0]['native']['value']['large']['lexeme'])

    def test_explicit_integral_yaml_float_is_already_supported(self):
        value = parse_yaml(b'num: !!float 1\n')
        self.assertIsInstance(value['num'], float)
        self.assertEqual(1.0, value['num'])

    def test_local_typescript_exports_keep_aliases_and_type_only_standing(self):
        source = 'function foo() {} function privateFn() {} type T = {x: number}; export {foo as renamed}; export type {T};'
        result = self.collection({'a.ts': source})
        self.assertFalse(collection_errors(result), result['diagnostics'])
        exports = self.facts(result, kind='local-export')
        self.assertEqual({'renamed', 'T'}, {f['native']['value']['exported_name'] for f in exports})
        by_name = {f['native']['value']['exported_name']: f['native']['value'] for f in exports}
        self.assertEqual('foo', by_name['renamed']['local_name'])
        self.assertFalse(by_name['renamed']['type_only'])
        self.assertTrue(by_name['T']['type_only'])
        public = {f['native']['value']['name'] for f in self.facts(result, kind='exported-declaration')}
        self.assertEqual({'foo', 'T'}, public)

    def test_ant_project_xml_is_not_maven(self):
        source = '<project name="ant"><target name="x"><dependency><artifactId>not-maven</artifactId></dependency></target></project>'
        result = self.collection({'build.xml': source})
        self.assertFalse(collection_errors(result))
        self.assertFalse(self.facts(result, 'maven.pom'))
        self.assertTrue(self.facts(result, 'xml.document', 'structured-document'))

    def test_unnamespaced_pom_requires_model_version_discriminator(self):
        source = '<project><modelVersion>4.0.0</modelVersion><dependencies><dependency><artifactId>demo</artifactId></dependency></dependencies></project>'
        result = self.collection({'pom.xml': source})
        self.assertFalse(collection_errors(result))
        self.assertTrue(self.facts(result, 'maven.pom', 'dependency'))

    def test_svg_uses_same_no_dtd_utf8_boundary_as_other_xml(self):
        source = '<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE svg [<!ENTITY x "forbidden">]><svg><title>&x;</title></svg>'
        result = self.collection({'bad.svg': source.encode('utf-16')})
        self.assertTrue(collection_errors(result))
        self.assertFalse(self.facts(result, 'svg.document-metadata'))
        good = self.collection({'good.svg': '<svg xmlns="http://www.w3.org/2000/svg"><title>Safe</title></svg>'})
        self.assertFalse(collection_errors(good))
        self.assertEqual('Safe', self.facts(good, 'svg.document-metadata')[0]['native']['value']['title'])
