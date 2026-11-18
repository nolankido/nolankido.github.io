"""Turn 10: source-backed HTML5 regression lesson and portable offline checker."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'downloads/website-check-reproduction.py'
RECORD = ROOT / 'downloads/website-check-evidence.json'
RUNBOOK = ROOT / 'downloads/website-check-offline-runbook.md'
SOURCE = ROOT / '_source/technology/checking-ai-website-changes.html'
BUILT = ROOT / 'technology/checking-ai-website-changes/index.html'


def checker():
    spec = importlib.util.spec_from_file_location('website_check_reproduction', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestWebsiteRepairTurn10(unittest.TestCase):
    def test_negative_control_identifies_exact_html5_failure(self):
        module = checker()
        bad, good = module.errors(module.BAD), module.errors(module.GOOD)
        self.assertTrue(module.expected_failure(bad))
        self.assertFalse(good)
        self.assertFalse(module.expected_failure(good))
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(module.main([]), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report['expected_error'],
                         {'code': 'end-tag-too-early', 'tag': 'div'})
        self.assertEqual(report['status'], 'pass')

    def test_optional_file_mode_accepts_valid_and_rejects_invalid(self):
        module = checker()
        with tempfile.TemporaryDirectory() as temporary:
            local = Path(temporary) / 'example.html'
            for content, result in ((module.GOOD, 0), (module.BAD, 1)):
                local.write_text(content, encoding='utf-8')
                with redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(module.main(['--file', str(local)]), result)
                report = json.loads(output.getvalue())
                self.assertEqual(report['status'], 'pass' if result == 0 else 'fail')
            local.unlink()
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(module.main(['--file', str(local)]), 2)
            self.assertEqual(json.loads(output.getvalue())['status'], 'read-error')

    def test_pinned_source_provenance_is_consistent(self):
        record = json.loads(RECORD.read_text(encoding='utf-8'))
        closure = record['source_closure']
        self.assertEqual(closure['path'], '_source/technology/task-brief.html')
        self.assertEqual(closure['pre_repair_ref'], record['pre_repair']['commit'])
        self.assertEqual(closure['repaired_ref'], record['repaired']['candidate'])
        self.assertEqual(closure['pre_repair_last_line'], '</div></div></section>')
        self.assertEqual(closure['repaired_last_line'], '</div></section>')
        self.assertNotEqual(closure['pre_repair_blob_sha'], closure['repaired_blob_sha'])
        for key in ('pre_repair_blob_sha', 'repaired_blob_sha'):
            self.assertRegex(closure[key], r'^[0-9a-f]{40}$')
        self.assertIn('not re-executed', record['limitations'][-1])

    def test_source_and_generated_case_link_to_real_evidence(self):
        source = SOURCE.read_text(encoding='utf-8')
        built = BUILT.read_text(encoding='utf-8')
        record = json.loads(RECORD.read_text(encoding='utf-8'))
        closure = record['source_closure']
        for content in (source, built):
            self.assertIn('id="case-source-diff"', content)
            self.assertIn('href="#case-source-diff"', content)
            self.assertIn('/downloads/website-check-offline-runbook.md', content)
            self.assertIn('python website-check-reproduction.py --file', content)
            for key in ('pre_repair_blob_sha', 'repaired_blob_sha'):
                self.assertIn(closure[key], content)

    def test_public_download_registration_and_runbook_scope(self):
        import sys
        sys.path.insert(0, str(ROOT / '_scripts'))
        import check_live
        targets = check_live.targets(ROOT)
        for route in ('/downloads/website-check-reproduction.py',
                      '/downloads/website-check-evidence.json',
                      '/downloads/website-check-offline-runbook.md'):
            self.assertEqual(targets[route][0], 200)
        guide = RUNBOOK.read_text(encoding='utf-8')
        self.assertIn('--file path/to/built/index.html', guide)
        self.assertIn('end-tag-too-early', guide)
        self.assertIn('No verified Google indexing', json.dumps(
            json.loads(RECORD.read_text(encoding='utf-8'))['limitations']))
        self.assertIn('Do not add or rely on GitHub Actions', guide)


if __name__ == '__main__':
    unittest.main()
