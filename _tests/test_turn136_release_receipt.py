"""Real Git worktrees and synthetic release steps test pinned local receipts."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import rebuild_release_candidate as gate


class ReleaseReceiptTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.parent = Path(tmp.name)
        self.root = self.parent / 'source'
        self.root.mkdir()
        self.target = self.parent / 'candidate'
        self.receipt = self.parent / 'receipt.jsonl'
        gate.git(self.root, 'init', '-q')
        (self.root / '_scripts').mkdir()
        self.script('build_books.py', 'from pathlib import Path\nPath("book.html").write_text("fixture")\n')
        self.script('build.py', 'from pathlib import Path\nPath("index.html").write_text("fixture")\n')
        self.script('prepare_local_release.py', 'from pathlib import Path\nPath("audit.json").write_text("fixture")\n')
        self.commit()

    def script(self, name, source):
        (self.root / '_scripts' / name).write_text(source, encoding='utf-8')

    def commit(self):
        gate.git(self.root, 'add', '.')
        gate.git(self.root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '-qm', 'fixture')
        self.head = gate.git(self.root, 'rev-parse', 'HEAD', capture=True)

    def run_release(self):
        return gate.rebuild(self.root, self.target, expected_head=self.head, receipt=self.receipt)

    def events(self):
        return [json.loads(line) for line in self.receipt.read_text(encoding='utf-8').splitlines()]

    def test_success_records_exact_head_steps_and_uncommitted_outputs(self):
        self.assertEqual(self.run_release(), self.target)
        events = self.events()
        self.assertEqual(events[0]['head'], self.head)
        self.assertEqual(events[0]['event'], 'started')
        self.assertEqual([e['step'] for e in events if e['event'] == 'step_pass'],
                         ['create detached worktree', '_scripts/build_books.py', '_scripts/build.py',
                          '_scripts/prepare_local_release.py --apply'])
        self.assertEqual(events[-1]['event'], 'finished')
        self.assertEqual(events[-1]['status'], 'pass')
        self.assertEqual(events[-1]['head'], self.head)
        self.assertFalse(events[-1]['deployment_verified'])
        self.assertIn('?? audit.json', events[-1]['worktree_status'])
        self.assertEqual(gate.git(self.root, 'status', '--porcelain', capture=True), '')

    def test_wrong_head_refuses_before_worktree_or_receipt(self):
        previous = self.head
        self.script('build.py', 'raise SystemExit(7)\n')
        self.commit()
        with self.assertRaisesRegex(gate.RebuildError, 'Reviewed commit mismatch'):
            gate.rebuild(self.root, self.target, expected_head=previous, receipt=self.receipt)
        self.assertFalse(self.target.exists())
        self.assertFalse(self.receipt.exists())

    def test_abbreviated_head_is_not_an_exact_pin(self):
        with self.assertRaisesRegex(gate.RebuildError, 'Reviewed commit mismatch'):
            gate.rebuild(self.root, self.target, expected_head=self.head[:8], receipt=self.receipt)
        self.assertFalse(self.target.exists())

    def test_failed_build_preserves_receipt_and_never_claims_success(self):
        self.script('build.py', 'raise SystemExit(7)\n')
        self.commit()
        with self.assertRaisesRegex(gate.RebuildError, 'Python exit 7'):
            self.run_release()
        self.assertTrue(self.target.is_dir())
        events = self.events()
        self.assertEqual(events[-1]['status'], 'blocked')
        self.assertEqual(events[-1]['step'], '_scripts/build.py')
        self.assertIn('Python exit 7', events[-1]['reason'])
        self.assertFalse(any(e.get('status') == 'pass' for e in events))
        self.assertFalse((self.target / 'audit.json').exists())

    def test_failed_full_validation_is_not_a_pass(self):
        self.script('prepare_local_release.py', 'raise SystemExit(9)\n')
        self.commit()
        with self.assertRaisesRegex(gate.RebuildError, 'Python exit 9'):
            self.run_release()
        self.assertEqual(self.events()[-1]['step'], '_scripts/prepare_local_release.py --apply')
        self.assertEqual(self.events()[-1]['status'], 'blocked')

    def test_existing_receipt_is_never_overwritten(self):
        self.receipt.write_text('keep', encoding='utf-8')
        with self.assertRaisesRegex(gate.RebuildError, 'new file'):
            self.run_release()
        self.assertEqual(self.receipt.read_text(encoding='utf-8'), 'keep')
        self.assertFalse(self.target.exists())

    def test_receipts_inside_either_checkout_are_refused(self):
        for path in (self.root / 'receipt.jsonl', self.target / 'receipt.jsonl',
                     self.parent / 'missing' / 'receipt.jsonl'):
            with self.subTest(path=path), self.assertRaisesRegex(gate.RebuildError, 'outside both checkouts'):
                gate.rebuild(self.root, self.target, receipt=path)
            self.assertFalse(path.exists())
            self.assertFalse(self.target.exists())


if __name__ == '__main__':
    unittest.main()
