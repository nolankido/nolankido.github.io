"""Turn 160: actual browser selection and fixture-versus-repository provenance.

The default Python regression test does not import Playwright. It executes
only the two pure helper functions from the real browser script's AST.
"""
from __future__ import annotations

import ast
import hashlib
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "_tests/poker_hand_review_content_browser.py"


def helpers(source: str, root: Path):
    tree = ast.parse(source)
    cases = next(ast.literal_eval(node.value) for node in tree.body
                 if isinstance(node, ast.Assign) and any(
                     isinstance(target, ast.Name) and target.id == 'CASES'
                     for target in node.targets))
    defs = [node for node in tree.body if isinstance(node, ast.FunctionDef) and
            node.name in ('repository_identity', 'browser_executable')]
    if len(defs) != 2:
        raise AssertionError('The two provenance/browser helpers are required')
    module = ast.Module(body=[ast.ImportFrom(module='__future__',
                         names=[ast.alias(name='annotations')], level=0), *defs],
                        type_ignores=[])
    ast.fix_missing_locations(module)
    context = {'ROOT': root, 'CASES': cases, 'os': os, 'hashlib': hashlib,
               'Path': Path, 'shutil': shutil, 'urlsplit': urlsplit}
    exec(compile(module, str(SCRIPT), 'exec'), context)
    return context


class BrowserProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SCRIPT.read_text(encoding='utf-8')

    def test_auto_detect_and_missing_browser_override(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            browser = root / 'chromium'
            browser.write_bytes(b'fake-executable')
            fn = helpers(self.script, root)['browser_executable']
            with patch.dict(os.environ, {'CHROMIUM_PATH': str(browser)}):
                self.assertEqual(fn(), str(browser))
            with patch.dict(os.environ, {'CHROMIUM_PATH': str(root / 'missing')}):
                with self.assertRaises(FileNotFoundError):
                    fn()
            with patch.dict(os.environ, {'CHROMIUM_PATH': ''}):
                with patch('shutil.which', side_effect=lambda name: str(browser)
                           if name == 'chromium' else None):
                    self.assertEqual(fn(), str(browser))
                with patch('shutil.which', return_value=None):
                    self.assertIsNone(fn())

    def test_fixture_is_distinguished_from_source_validated_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ctx = helpers(self.script, root)
            for origin, _anchor, lesson in ctx['CASES']:
                for route in (origin, urlsplit(lesson).path):
                    path = root / route.lstrip('/') / 'index.html'
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text('<main>fixture page</main>', encoding='utf-8')
            with patch.dict(os.environ, {'POKER_BROWSER_REQUIRE_REPO': ''}):
                result = ctx['repository_identity']()
                self.assertEqual(result['root_type'], 'synthetic_or_incomplete_fixture')
                self.assertFalse(result['source_ownership_checked'])
                self.assertFalse(result['production_deployment_checked'])
                self.assertEqual(len(result['source_pages_sha256']), 4)
            with patch.dict(os.environ, {'POKER_BROWSER_REQUIRE_REPO': '1'}):
                with self.assertRaisesRegex(RuntimeError, 'fixture root'):
                    ctx['repository_identity']()
            for name in ('AGENTS.md', '_source/pages.json', '_scripts/build.py',
                         '_scripts/build_poker_episode.py', '_scripts/build_standoff_episode.py'):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('marker\n', encoding='utf-8')
            for slug in ('portland-meadows-ep1', 'portland-meadows-standoff'):
                source = root / '_source/poker' / (slug + '.html')
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text('<article>source marker</article>', encoding='utf-8')
                published = root / 'poker/episodes' / slug / 'index.html'
                published.write_text('<header></header><article>source marker</article>', encoding='utf-8')
            with patch.dict(os.environ, {'POKER_BROWSER_REQUIRE_REPO': '1'}):
                result = ctx['repository_identity']()
                self.assertEqual(result['root_type'], 'checked_out_repository')
                self.assertTrue(result['source_ownership_checked'])
            source = root / '_source/poker/portland-meadows-standoff.html'
            source.write_text('<article>not found in published</article>')
            with self.assertRaisesRegex(ValueError, 'Standalone source-to-published mismatch'):
                ctx['repository_identity']()

    def test_browser_script_remains_offline_and_has_accurate_labels(self):
        for s in ('synthetic_fixture_smoke_pass', 'checked_out_repository_render_pass',
                  'production_deployment_checked', 'POKER_BROWSER_REQUIRE_REPO',
                  'browser_executable', 'source_pages_sha256'):
            self.assertIn(s, self.script)
        self.assertNotIn('page.goto(', self.script)
        self.assertIn('page.set_content(local_document(route)', self.script)
        self.assertIn('context.route("**/*", block)', self.script)
        self.assertNotIn('\u2014', self.script)


if __name__ == '__main__':
    unittest.main()
