"""PR 111 closure regressions. Usage: python -m unittest tests.test_native_review_closure."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from msdmd.collect import collect, collection_errors
from msdmd.readers import implementation_digest
import msdmd.readers as readers


class NativeReviewClosure(unittest.TestCase):
    def collection(self, files, **options):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name, content in files.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content.encode() if isinstance(content, str) else content)
            return collect(root, 'fixture', source_commit='a' * 40, **options)

    def facts(self, result, kind=None):
        return [fact for fact in result['facts'] if kind is None or fact['kind'] == kind]

    def test_xml_sensitive_tags_and_namespaced_attributes_are_redacted(self):
        sources = [
            '<config><api_token>DO_NOT_PUBLISH_1</api_token><safe>visible</safe></config>',
            '<config xmlns:x="urn:config"><x:password>DO_NOT_PUBLISH_2<child>DO_NOT_PUBLISH_3</child></x:password></config>',
            '<config xmlns:x="urn:config" x:api_token="DO_NOT_PUBLISH_4"><safe>visible</safe></config>',
            '<api_token><testsuite><testcase name="DO_NOT_PUBLISH_5"/></testsuite></api_token>',
        ]
        for source in sources:
            with self.subTest(source=source):
                result = self.collection({'config.xml': source})
                self.assertFalse(collection_errors(result), result['diagnostics'])
                self.assertNotIn('DO_NOT_PUBLISH', json.dumps(result))
                self.assertIn('sensitive_fields_redacted', {d['code'] for d in result['diagnostics']})
                self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), self.facts(result)[0]['source']['content_sha256'])

    def test_xml_unrelated_content_is_preserved(self):
        result = self.collection({'config.xml': '<config><name>demo</name><safe>visible</safe></config>'})
        self.assertFalse(collection_errors(result))
        self.assertIn('visible', json.dumps(result))
        self.assertNotIn('sensitive_fields_redacted', {d['code'] for d in result['diagnostics']})

    def test_default_export_assignment_links_the_named_symbol(self):
        for expression in ('foo', '(foo)'):
            result = self.collection({'a.ts': 'function foo() {} function privateFn() {} export default ' + expression + ';'})
            self.assertFalse(collection_errors(result), result['diagnostics'])
            exported = self.facts(result, 'exported-declaration')
            self.assertEqual(['foo'], [f['native']['value']['name'] for f in exported])
            binding = self.facts(result, 'local-export')[0]['native']['value']
            self.assertEqual('default', binding['exported_name'])
            self.assertEqual([exported[0]['native']['value']['identity']], binding['declaration_identities'])

    def test_named_and_anonymous_default_declarations_are_explicit(self):
        for source in ('export default function foo() {}', 'export default function() {}',
                       'export default class Named {}', 'export default class {}'):
            with self.subTest(source=source):
                result = self.collection({'a.ts': source})
                self.assertFalse(collection_errors(result), result['diagnostics'])
                declarations = self.facts(result, 'exported-declaration')
                self.assertEqual(1, len(declarations))
                self.assertIn('default', declarations[0]['native']['value']['export_names'])
                if declarations[0]['native']['value'].get('anonymous'):
                    self.assertIsNone(declarations[0]['native']['id'])
                self.assertEqual('default', self.facts(result, 'local-export')[0]['native']['value']['exported_name'])

    def test_default_expression_and_export_equals_are_not_dropped(self):
        for source, name in [('export default 42;', 'default'), ('export default () => 42;', 'default'),
                             ('const foo = {}; export = foo;', 'export=')]:
            result = self.collection({'a.ts': source})
            self.assertFalse(collection_errors(result), result['diagnostics'])
            self.assertEqual(name, self.facts(result, 'local-export')[0]['native']['value']['exported_name'])

    def test_literal_python_exports_remain_static(self):
        result = self.collection({'a.py': "__all__ = ['a']\ndef a(): pass\n"}, required_sources=['a.py'])
        self.assertFalse(collection_errors(result), result['diagnostics'])
        value = self.facts(result, 'exports')[0]['native']['value']
        self.assertEqual('static', value['resolution'])
        self.assertEqual(['a'], value['names'])

    def test_mutated_or_escaped_python_exports_are_partial(self):
        mutations = ["__all__.append('b')", "__all__ += ['b']", "__all__[0] = 'b'", "del __all__[0]",
                     "alias = __all__; alias.append('b')", "if enabled: __all__ = ['b']", "__all__ = ['b']",
                     "mutate(__all__)"]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                result = self.collection({'a.py': "__all__ = ['a']\n" + mutation + '\n'}, required_sources=['a.py'])
                self.assertTrue(collection_errors(result))
                self.assertIn('dynamic_python_exports', {d['code'] for d in result['diagnostics']})
                self.assertTrue(all(f['native']['value']['resolution'] != 'static' for f in self.facts(result, 'exports')))
                self.assertEqual('partial', next(d['status'] for d in result['discovery'] if d['file'] == 'a.py'))

    def test_conditional_only_python_exports_are_unresolved(self):
        result = self.collection({'a.py': "if enabled: __all__ = ['a']\n"}, required_sources=['a.py'])
        self.assertTrue(collection_errors(result))
        self.assertIn('dynamic_python_exports', {d['code'] for d in result['diagnostics']})

    def test_repeated_spdx_headers_have_distinct_addresses(self):
        sources = {
            'a.py': '# SPDX-FileCopyrightText: 2020 A\n# SPDX-FileCopyrightText: 2021 B\n\ndef f(): pass\n',
            'a.ts': '/* SPDX-FileCopyrightText: 2020 A\n * SPDX-FileCopyrightText: 2021 B\n */\nexport const f = 1;\n',
        }
        for name, source in sources.items():
            with self.subTest(name=name):
                result = self.collection({name: source})
                self.assertFalse(collection_errors(result), result['diagnostics'])
                licenses = self.facts(result, 'license-declaration')
                self.assertEqual(2, len(licenses))
                self.assertEqual(2, len({f['address'] for f in licenses}))
                self.assertEqual({'2020 A', '2021 B'}, {f['native']['value']['value'] for f in licenses})

    def test_typescript_comments_use_innermost_symbol_even_in_empty_bodies(self):
        source = """// module-only
function outer() {
  // outer-note
  function inner() {
    // inner-note
  }
  // outer-end
}
class Box {
  // class-note
  method() {
    // method-note
  }
}
"""
        result = self.collection({'a.ts': source})
        self.assertFalse(collection_errors(result), result['diagnostics'])
        comments = {f['native']['value']['text'].strip(): f for f in self.facts(result, 'comment')}
        self.assertEqual('module', comments['// module-only']['subject']['scope'])
        for text, expected in [('// outer-note', 'outer#0'), ('// inner-note', 'outer.inner#0'),
                               ('// outer-end', 'outer#0'), ('// class-note', 'Box#0'), ('// method-note', 'Box.method#0')]:
            self.assertIn(text, comments)
            self.assertEqual('symbol', comments[text]['subject']['scope'])
            self.assertEqual(expected, comments[text]['subject']['identity'])

    def test_typescript_literal_comment_lookalikes_are_not_comments(self):
        source = r'const x = "// not-a-comment"; const y = `/* not-a-comment */`; const z = /\/\/not-a-comment/;'
        result = self.collection({'a.ts': source})
        self.assertFalse(collection_errors(result), result['diagnostics'])
        self.assertFalse(self.facts(result, 'comment'))

    def test_reader_identity_changes_when_universal_parser_changes(self):
        implementation_digest.cache_clear()
        original = implementation_digest()
        path = Path(readers.__file__).parent / 'parsers' / 'universal.py'
        read_bytes = Path.read_bytes
        def changed(source):
            data = read_bytes(source)
            return data + b'\n# executable reader dependency changed\n' if source == path else data
        try:
            implementation_digest.cache_clear()
            with patch.object(Path, 'read_bytes', changed):
                self.assertNotEqual(original, implementation_digest())
        finally:
            implementation_digest.cache_clear()

    def test_gitignore_trailing_spaces_follow_git_escaping(self):
        slash = chr(92)
        source = '   \nfoo   \nbar' + slash + '  \npath/   \n!keep   \n' + slash + '#literal   \n' + slash + '!literal   \n'
        result = self.collection({'.gitignore': source})
        self.assertFalse(collection_errors(result))
        rules = [f['native']['value'] for f in self.facts(result, 'ignore-rule')]
        self.assertEqual(['foo', 'bar' + slash + ' ', 'path/', 'keep', slash + '#literal', slash + '!literal'],
                         [rule['pattern'] for rule in rules])
        self.assertEqual([1, 2, 3, 4, 5, 6], [rule['order'] for rule in rules])
        self.assertTrue(rules[2]['directory_only'])
        self.assertTrue(rules[3]['negated'])
        self.assertFalse(rules[5]['negated'])
