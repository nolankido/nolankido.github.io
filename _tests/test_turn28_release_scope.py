"""Turn 28: narrow read-only release checks never change the allowed origins or invent routes."""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '_scripts/check_live.py'
DOWNLOAD = ROOT / 'downloads/gsc-period-compare.py'


class NarrowReleaseScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.source, filename=str(SCRIPT))
        selection = [n for n in cls.tree.body if isinstance(n, ast.FunctionDef)
                     and n.name == 'selected_targets']
        if len(selection) != 1:
            raise AssertionError('exactly one selected_targets function required')
        isolated = ast.Module(body=selection, type_ignores=[])
        ast.fix_missing_locations(isolated)
        namespace = {}
        exec(compile(isolated, '<selected-targets>', 'exec'), namespace)
        cls.select = staticmethod(namespace['selected_targets'])

    def test_one_route_is_scoped_without_changing_expected_bytes(self):
        checks = {'/': (200, b'index'), '/downloads/gsc-period-compare.py': (200, b'code'),
                  '/downloads/gsc-monthly-local-audit.py': (200, b'old')}
        chosen = self.select(checks, ['/downloads/gsc-period-compare.py'])
        self.assertEqual(chosen, {'/downloads/gsc-period-compare.py': (200, b'code')})
        self.assertIs(chosen['/downloads/gsc-period-compare.py'], checks['/downloads/gsc-period-compare.py'])

    def test_multiple_routes_preserve_requested_order(self):
        checks = {'/a': (200, b'A'), '/b': (200, b'B'), '/c': (200, b'C')}
        self.assertEqual(list(self.select(checks, ['/c', '/a'])), ['/c', '/a'])

    def test_no_filter_leaves_existing_full_verifier_unchanged(self):
        checks = {'/': (200, b'index')}
        self.assertIs(self.select(checks, None), checks)

    def test_duplicates_are_rejected(self):
        checks = {'/': (200, b'index')}
        with self.assertRaisesRegex(ValueError, '[Dd]uplicate'):
            self.select(checks, ['/', '/'])

    def test_unknown_and_external_routes_are_rejected(self):
        checks = {'/': (200, b'index')}
        for bad in ('/missing', 'https://evil.example/', '//evil.example/',
                    '/?sneaky=1', '/#anchor', ''):
            with self.subTest(route=bad), self.assertRaises(ValueError):
                self.select(checks, [bad])

    def test_cli_wires_option_to_selected_targets(self):
        main = next(n for n in self.tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
        arguments = [n for n in ast.walk(main) if isinstance(n, ast.Call) and
                     isinstance(n.func, ast.Attribute) and n.func.attr == 'add_argument']
        self.assertTrue(any(any(isinstance(a, ast.Constant) and a.value == '--only'
                                for a in n.args) for n in arguments))
        self.assertIn('selected_targets(targets(), args.only)', ast.get_source_segment(self.source, main))
        self.assertIn('parser.error(str(error))', ast.get_source_segment(self.source, main))

    def test_exact_byte_and_status_checks_still_exist(self):
        self.assertIn('status != expected[0]', self.source)
        self.assertIn('body != expected[1]', self.source)
        self.assertIn("method='GET'", self.source)
        self.assertIn("ORIGIN = 'https://nolankido.com'", self.source)
        self.assertIn('SameOriginRedirect', self.source)
        self.assertIn("'downloads/gsc-period-compare.py'", self.source)
        self.assertTrue(DOWNLOAD.is_file())


if __name__ == '__main__':
    unittest.main()
