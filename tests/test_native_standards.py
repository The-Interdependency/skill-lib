"""End-to-end native reader fixtures: run python -m unittest tests.test_native_standards.

All source metadata is supplied as inert fixture bytes. Tests distinguish syntax
extraction, required information, source identity and claimed runtime evidence.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from msdmd.collect import collect, collection_errors
from msdmd.formats import parse_json, parse_yaml, parse_xml
from msdmd.module_projection import project_python_bytes
from msdmd.readers import read_native

ROOT = Path(__file__).resolve().parents[1]


class NativeStandardsTests(unittest.TestCase):
    def collection(self, files: dict[str, str | bytes], **options):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content.encode() if isinstance(content, str) else content)
            return collect(root, 'fixture', source_commit='a' * 40, **options)

    def facts(self, result, namespace=None, kind=None):
        return [f for f in result['facts'] if (namespace is None or f['convention']['namespace'] == namespace)
                and (kind is None or f['kind'] == kind)]

    def test_yaml_core_nested_aliases_and_typed_keys_are_preserved(self):
        value = parse_yaml(b'on: [push]\nx: &x {yes: true, no: false}\ny: *x\nnum: !!float 1\nresponse: {200: ok, "200": other}\n')
        self.assertEqual(['push'], value['on'])
        self.assertEqual({'yes': True, 'no': False}, value['x'])
        self.assertEqual(value['x'], value['y'])
        self.assertIsInstance(value['num'], float)
        self.assertEqual('yaml-mapping', value['response']['$type'])
        self.assertEqual([200, '200'], [v['key'] for v in value['response']['entries']])
        self.assertEqual({'text': 'false'}, parse_yaml(b'text: !!str false\n'))

    def test_unsafe_or_ambiguous_serializations_are_rejected(self):
        cases = [(parse_json, b'{"a":1,"a":2}'), (parse_json, b'{"x":NaN}'),
                 (parse_json, b'{"x":1e999}'), (parse_yaml, b'x: 1\nx: 2'),
                 (parse_yaml, b'x: &a [*a]'), (parse_yaml, b'x: !unsafe data'),
                 (parse_yaml, b'x: {<<: {a: 1}}'), (parse_yaml, b'x: !!bool 1'),
                 (parse_xml, b'<!DOCTYPE r [<!ENTITY e SYSTEM "file:///etc/passwd">]><r>&e;</r>')]
        for parser, source in cases:
            with self.subTest(source=source):
                with self.assertRaises(Exception): parser(source)

    def test_frontmatter_full_structure_is_available_without_redeclaration(self):
        result = self.collection({'SKILL.md': '---\nname: example\ninputs:\n  - name: thing\n    required: true\n---\n# Usage\n'})
        self.assertFalse(collection_errors(result))
        self.assertEqual([], result['declarations'])
        self.assertIn('inputs', self.facts(result, 'markdown.yaml-frontmatter')[0]['native']['value']['fields'])

    def test_python_docstring_dialects_emit_structured_parameters(self):
        docs = {
            'sphinx': ':param value: The input.\n:type value: int\n:returns: Twice.\n:rtype: int',
            'google': 'Args:\n    value (int): The input.\n\nReturns:\n    int: Twice.',
            'numpy': 'Parameters\n----------\nvalue : int\n    The input.\n\nReturns\n-------\nint\n    Twice.'}
        for name, doc in docs.items():
            with self.subTest(dialect=name):
                code = 'def double(value: int) -> int:\n    """Double.\n\n' + '\n'.join('    ' + line for line in doc.split('\n')) + '\n    """\n    return value * 2\n'
                result = self.collection({'a.py': code})
                fact = self.facts(result, 'python.pep257', 'documentation')[0]
                self.assertEqual('double', fact['subject']['identity'])
                self.assertTrue(any(v.get('arg_name') == 'value' for v in fact['native']['value']['fields']))
                self.assertFalse(collection_errors(result))

    def test_python_shared_attachment_and_blank_line_identity(self):
        code = '# leading note\ndef run(x: int):\n    # interior note\n    return x\n'
        first = self.collection({'a.py': code})
        second = self.collection({'a.py': '\n\n' + code})
        for kind in ('callable-declaration', 'comment'):
            self.assertEqual([v['address'] for v in self.facts(first, kind=kind)], [v['address'] for v in self.facts(second, kind=kind)])
        self.assertNotEqual(first['source']['snapshot_sha256'], second['source']['snapshot_sha256'])
        projection = project_python_bytes(code.encode(), source_path='a.py', repo='fixture', revision='a' * 40)
        self.assertTrue(any(v['record_type'] == 'metadata' and v['text'] == 'leading note' for v in projection))
        for fact in self.facts(first, kind='comment'):
            self.assertEqual('run', fact['subject']['identity'])

    def test_python_never_executes_fixture_or_dynamic_exports(self):
        result = self.collection({'a.py': 'raise RuntimeError("must not run")\n__all__ = get_names()\n'})
        self.assertFalse(collection_errors(result))
        self.assertIn('dynamic_python_exports', {d['code'] for d in result['diagnostics']})
        self.assertEqual('partial', next(v['status'] for v in result['discovery'] if v['file'] in {'a.py', 'a.ts', 'api.json'}))

    def test_typescript_multiline_members_jsdoc_tags_and_string_fences(self):
        code = '''const fixture = `// === DOCS ===
// id: fake
// === END DOCS ===`;
export class Client {
  /** Read a value.
   * @param name The requested name.
   * @returns Its value.
   * @custom preserved
   */
  read(
    name: string
  ): number { return 1; }
}
'''
        result = self.collection({'a.ts': code})
        self.assertFalse(collection_errors(result), result['diagnostics'])
        self.assertFalse(result['declarations'])
        docs = self.facts(result, 'typescript.documentation-comment')
        self.assertTrue(any('read' in f['subject']['identity'] for f in docs))
        self.assertIn('custom', json.dumps(docs))

    def test_missing_typescript_runtime_is_unsupported_not_empty_success(self):
        with patch('msdmd.native_code.subprocess.run', side_effect=FileNotFoundError()):
            result = self.collection({'a.ts': 'export const x = 1;'}, required_sources=['*.ts'])
        self.assertTrue(collection_errors(result))
        self.assertIn('reader_dependency_unavailable', {d['code'] for d in result['diagnostics']})
        self.assertEqual('unsupported', next(v['status'] for v in result['discovery'] if v['file'] in {'a.py', 'a.ts', 'api.json'}))

    def test_native_source_language_documentation_and_symbol_attachment(self):
        fixtures = {'a.rs': ('/// Double.\npub fn double(x: i32) -> i32 { x*2 }\n', 'rustdoc', 'double'),
            'A.java': ('public class A {\n/** Read.\n * @param x value\n */\n public int read(int x) { return x; }\n}\n', 'javadoc', 'A.read'),
            'a.c': ('/** Double.\n * @param x value\n */\nint twice(int x) { return x*2; }\n', 'doxygen', 'twice'),
            'a.hpp': ('class A { public:\n/** Read. */\nint read(int x) { return x; }\n};', 'doxygen', 'A.read')}
        for path, (source, namespace, identity) in fixtures.items():
            with self.subTest(language=path):
                result = self.collection({path: source})
                self.assertFalse(collection_errors(result), result['diagnostics'])
                docs = self.facts(result, namespace, 'documentation-comment')
                self.assertEqual(identity, docs[0]['subject']['identity'])

    def test_ambiguous_headers_and_macro_context_remain_visible(self):
        result = self.collection({'a.h': 'int x;', 'a.rs': 'foo!();'}, required_sources=['a.h'])
        self.assertTrue(collection_errors(result))
        self.assertTrue({'ambiguous_header_language', 'unresolved_compile_context'}.issubset({d['code'] for d in result['diagnostics']}))

    def test_source_spdx_headers_are_actual_comments(self):
        result = self.collection({'a.rs': '// SPDX-License-Identifier: MIT\npub fn f() {}'})
        self.assertEqual('MIT', self.facts(result, 'spdx.source-header')[0]['native']['value']['value'])

    def test_openapi_yaml_operations_and_local_or_external_refs(self):
        result = self.collection({'api.yaml': 'openapi: 3.1.0\ninfo: {title: test, version: "1"}\npaths:\n  /items:\n    get:\n      operationId: listItems\n      responses:\n        "200":\n          $ref: other.json#/response\n'})
        self.assertFalse(collection_errors(result))
        operation = self.facts(result, 'openapi.document', 'api-operation')[0]
        self.assertEqual('listItems', operation['native']['id'])
        self.assertEqual('paths:GET /items', operation['subject']['identity'])
        self.assertEqual(False, self.facts(result, 'metadata.reference')[0]['native']['value']['network_access'])

    def test_json_schema_unknown_fields_and_citation(self):
        result = self.collection({'s.json': json.dumps({'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': 'urn:example', 'type': 'object', 'x-custom': [1, True]}),
            'CITATION.cff': 'cff-version: 1.2.0\ntitle: Example\nauthors:\n  - family-names: Example\ndoi: 10.123/example\n'})
        self.assertFalse(collection_errors(result))
        self.assertEqual([1, True], self.facts(result, 'json.schema')[0]['native']['value']['x-custom'])
        self.assertEqual('10.123/example', self.facts(result, 'citation.cff')[0]['native']['id'])

    def test_unknown_standard_versions_do_not_satisfy_required_policy(self):
        result = self.collection({'api.json': '{"openapi":"99.0.0","paths":{}}'}, required_sources=['api.json'])
        self.assertTrue(collection_errors(result))
        self.assertEqual('partial', next(v['status'] for v in result['discovery'] if v['file'] in {'a.py', 'a.ts', 'api.json'}))
        self.assertTrue(self.facts(result, 'openapi.document', 'api-description'))
        self.assertFalse(self.facts(result, 'openapi.document', 'api-operation'))

    def test_sarif_and_junit_are_reported_evidence_not_verified_behavior(self):
        result = self.collection({'scan.sarif': json.dumps({'version': '2.1.0', 'runs': [{'tool': {'driver': {'name': 'test'}}, 'results': [{'ruleId': 'X', 'message': {'text': 'problem'}}]}]}),
            'junit.xml': '<testsuite name="s"><testcase name="a"/><testcase name="b"><failure message="bad"/></testcase></testsuite>'})
        self.assertFalse(collection_errors(result))
        self.assertEqual('reported-evidence', self.facts(result, 'sarif', 'analysis-result')[0]['standing'])
        self.assertEqual(['reported-pass', 'failure'], [f['native']['value']['result'] for f in self.facts(result, 'junit.xml', 'test-result')])
        self.assertEqual('not-evaluated', result['coverage']['verified_behavior'])

    def test_spdx_and_cyclonedx_artifacts_preserve_native_ids(self):
        result = self.collection({'bom.json': json.dumps({'spdxVersion': 'SPDX-2.3', 'SPDXID': 'SPDXRef-DOCUMENT', 'packages': [{'SPDXID': 'SPDXRef-pkg', 'name': 'pkg'}]}),
            'cyclone.json': json.dumps({'bomFormat': 'CycloneDX', 'specVersion': '1.6', 'components': [{'bom-ref': 'pkg', 'name': 'pkg', 'components': [{'bom-ref': 'child', 'name': 'child'}]}]})})
        self.assertFalse(collection_errors(result))
        self.assertEqual('SPDXRef-pkg', self.facts(result, 'spdx.json', 'artifact-package')[0]['native']['id'])
        self.assertEqual(2, len(self.facts(result, 'cyclonedx.json', 'artifact-component')))

    def test_duplicate_native_ids_are_reported_without_dropping_witnesses(self):
        result = self.collection({'api.json': json.dumps({'openapi': '3.1.0', 'paths': {'/a': {'get': {'operationId': 'same'}}, '/b': {'get': {'operationId': 'same'}}}})})
        self.assertEqual(2, len(self.facts(result, 'openapi.document', 'api-operation')))
        self.assertIn('duplicate_native_identifier', {d['code'] for d in collection_errors(result)})

    def test_dsse_statement_is_decoded_without_signature_claim(self):
        statement = {'_type': 'https://in-toto.io/Statement/v1', 'subject': [{'name': 'app', 'digest': {'sha256': 'a'*64}}], 'predicateType': 'example', 'predicate': {}}
        result = self.collection({'att.json': json.dumps({'payloadType': 'application/vnd.in-toto+json', 'payload': base64.b64encode(json.dumps(statement).encode()).decode(), 'signatures': []})})
        self.assertFalse(collection_errors(result))
        self.assertEqual('app', self.facts(result, 'in-toto.statement', 'attested-subject')[0]['native']['id'])
        self.assertIn('unverified_signature', {d['code'] for d in result['diagnostics']})

    def test_package_manifests_lockfiles_and_reuse_are_integrated(self):
        result = self.collection({'Cargo.toml': '[package]\nname="demo"\n[dependencies]\nx="1"\n[target."cfg(unix)".build-dependencies]\ny="2"\n',
            'Cargo.lock': 'version=3\n[[package]]\nname="x"\nversion="1.0"\n',
            'package-lock.json': '{"lockfileVersion":3,"packages":{"node_modules/x":{"version":"1.0"}}}',
            'REUSE.toml': 'version=1\n[[annotations]]\npath="src/**"\nSPDX-License-Identifier="MIT"\n'})
        self.assertFalse(collection_errors(result))
        self.assertEqual(2, len(self.facts(result, 'cargo.manifest', 'dependency')))
        self.assertEqual(1, len(self.facts(result, 'cargo.lockfile', 'locked-package')))
        self.assertEqual(1, len(self.facts(result, 'npm.lockfile', 'locked-package')))
        self.assertEqual(1, len(self.facts(result, 'reuse.toml', 'license-rule')))

    def test_codeowners_precedence_and_ownerless_exemption(self):
        result = self.collection({'CODEOWNERS': '* @ignored\n', '.github/CODEOWNERS': '* @team\n/docs/\n'})
        self.assertFalse(collection_errors(result))
        rules = self.facts(result, 'github.codeowners', 'review-ownership')
        self.assertEqual(3, len(rules))
        self.assertTrue(any(f['native']['value']['owners'] == [] for f in rules))
        self.assertIn('shadowed', json.dumps(rules))

    def test_doxygen_dotnet_and_maven_xml(self):
        files = {'doc.xml': '<doxygen version="1.9"><compounddef id="A"><memberdef id="A_f"><name>f</name></memberdef></compounddef></doxygen>',
            'net.xml': '<doc><members><member name="M:A.F"><summary>F.</summary></member></members></doc>',
            'pom.xml': '<project xmlns="http://maven.apache.org/POM/4.0.0"><dependencies><dependency><groupId>g</groupId><artifactId>a</artifactId><version>1</version></dependency></dependencies></project>'}
        result = self.collection(files)
        self.assertFalse(collection_errors(result))
        for namespace, kind in [('doxygen.xml', 'documented-symbol'), ('dotnet.xml-doc', 'documented-symbol'), ('maven.pom', 'dependency')]:
            self.assertTrue(self.facts(result, namespace, kind))

    def test_required_facts_are_witnessed_and_missing_information_fails(self):
        policy = [{'file': '*.json', 'convention': 'npm.package-json', 'kind': 'dependency'}]
        ok = self.collection({'package.json': '{"dependencies":{"x":"1"}}'}, required_facts=policy)
        missing = self.collection({'package.json': '{"name":"empty"}'}, required_facts=policy)
        self.assertFalse(collection_errors(ok))
        self.assertTrue(collection_errors(missing))
        self.assertEqual('policy-evaluated', ok['coverage']['information_availability'])
        self.assertEqual('provided', ok['requirements'][0]['status'])

    def test_source_discovery_reports_limits_symlinks_and_exclusions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'large.json').write_text('x'*100)
            (root / 'secret.env').write_text('secret')
            (root / '.env').write_text('secret')
            (root / 'link.json').symlink_to('/etc/passwd')
            (root / 'node_modules').mkdir()
            result = collect(root, 'fixture', source_commit='a'*40, max_file_bytes=10, required_sources=['large.json'])
        ledger = {v['file']: v['status'] for v in result['discovery']}
        self.assertEqual('excluded', ledger['.env'])
        self.assertNotIn('secret', json.dumps(result['facts']))
        self.assertNotEqual('supported', ledger['link.json'])
        self.assertEqual(1, result['coverage']['excluded_subtrees'])
        self.assertTrue(collection_errors(result))

    def test_large_collection_chunks_roundtrip_without_code_execution(self):
        from msdmd.collect import render_typescript
        from msdmd.visualize import load_collection
        result = self.collection({'a.py': "\n".join(f"def f{i}(): return {i}" for i in range(70))})
        text = render_typescript(result, import_path='./collection')
        self.assertIn('mergeMsdmdFactChunks', text)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'collection.ts'
            path.write_text(text)
            self.assertEqual(result, load_collection(path))
            path.write_text('export default defineMsdmdCollectionV2({facts: mergeMsdmdFactChunks(evil())});')
            with self.assertRaises((ValueError, json.JSONDecodeError)):
                load_collection(path)

    def test_snapshot_replay_and_cli_drift_do_not_depend_on_git_head(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'a.json').write_text('{"x":1}')
            output = root / 'fixture_msdmd.ts'
            args = [sys.executable, '-m', 'msdmd.collect', '--root', str(root), '--repo', 'fixture', '--snapshot-identity', '--out', str(output)]
            self.assertEqual(0, subprocess.run(args, cwd=ROOT, capture_output=True).returncode)
            self.assertEqual(0, subprocess.run(args + ['--check'], cwd=ROOT, capture_output=True).returncode)
            (root / '__pycache__').mkdir()
            self.assertEqual(0, subprocess.run(args + ['--check'], cwd=ROOT, capture_output=True).returncode)
            (root / 'a.json').write_text('{"x":2}')
            self.assertEqual(1, subprocess.run(args + ['--check'], cwd=ROOT, capture_output=True).returncode)


if __name__ == '__main__':
    unittest.main()
