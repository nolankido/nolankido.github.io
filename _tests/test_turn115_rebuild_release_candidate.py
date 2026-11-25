"""Real local Git worktree controls using synthetic build/release subprocesses."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import rebuild_release_candidate as gate


class RebuildTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.parent = Path(temp.name)
        self.repo = self.parent / 'source'
        self.repo.mkdir()
        self.target = self.parent / 'candidate'
        gate.git(self.repo, 'init', '-q')
        (self.repo / '_scripts').mkdir()
        (self.repo / 'source.txt').write_text('reviewed source', encoding='utf-8')
        self.script('build_books.py', 'from pathlib import Path\nPath("book.html").write_text("built book")\n')
        self.script('build.py', 'from pathlib import Path\nassert Path("book.html").read_text() == "built book"\nPath("site.html").write_text(Path("source.txt").read_text())\n')
        self.script('prepare_local_release.py', 'from pathlib import Path\nimport sys\nif sys.argv[1:] != ["--apply"] or Path("site.html").read_text() != "reviewed source":\n    raise SystemExit(9)\nPath("audit.json").write_text("fixture audit")\n')
        self.commit()

    def script(self, name, source):
        (self.repo / '_scripts' / name).write_text(source, encoding='utf-8')

    def commit(self):
        gate.git(self.repo, 'add', '.')
        gate.git(self.repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '-qm', 'fixture')

    def test_real_detached_worktree_builds_and_preserves_local_edits(self):
        head = gate.git(self.repo, 'rev-parse', 'HEAD', capture=True)
        (self.repo / 'source.txt').write_text('uncommitted edit', encoding='utf-8')
        status = gate.git(self.repo, 'status', '--porcelain', capture=True)
        self.assertEqual(gate.rebuild(self.repo, self.target), self.target)
        self.assertEqual(gate.git(self.target, 'rev-parse', 'HEAD', capture=True), head)
        self.assertEqual((self.target / 'site.html').read_text(), 'reviewed source')
        self.assertEqual((self.target / 'audit.json').read_text(), 'fixture audit')
        self.assertEqual((self.repo / 'source.txt').read_text(), 'uncommitted edit')
        self.assertEqual(gate.git(self.repo, 'status', '--porcelain', capture=True), status)
        self.assertFalse((self.repo / 'book.html').exists())
        self.assertFalse((self.repo / 'audit.json').exists())
        self.assertNotEqual(subprocess.run(['git', '-C', str(self.target), 'symbolic-ref', '-q', 'HEAD'], check=False).returncode, 0)

    def test_failed_builder_leaves_candidate_and_never_runs_release(self):
        self.script('build.py', 'raise SystemExit(7)\n')
        self.commit()
        with self.assertRaisesRegex(gate.RebuildError, 'build.py'):
            gate.rebuild(self.repo, self.target)
        self.assertTrue((self.target / 'book.html').exists())
        self.assertFalse((self.target / 'audit.json').exists())
        self.assertEqual(gate.git(self.repo, 'status', '--porcelain', capture=True), '')

    def test_failed_release_retains_generated_evidence(self):
        self.script('prepare_local_release.py', 'raise SystemExit(8)\n')
        self.commit()
        with self.assertRaisesRegex(gate.RebuildError, 'prepare_local_release.py'):
            gate.rebuild(self.repo, self.target)
        self.assertTrue((self.target / 'site.html').exists())
        self.assertFalse((self.repo / 'site.html').exists())

    def test_existing_destination_is_never_overwritten(self):
        self.target.mkdir()
        marker = self.target / 'keep.txt'
        marker.write_text('keep')
        with self.assertRaisesRegex(gate.RebuildError, 'must not exist'):
            gate.rebuild(self.repo, self.target)
        self.assertEqual(marker.read_text(), 'keep')

    def test_nested_checkout_is_rejected(self):
        with self.assertRaisesRegex(gate.RebuildError, 'outside'):
            gate.rebuild(self.repo, self.repo / 'candidate')
        self.assertFalse((self.repo / 'candidate').exists())

    def test_missing_parent_is_rejected(self):
        with self.assertRaisesRegex(gate.RebuildError, 'parent directory'):
            gate.rebuild(self.repo, self.parent / 'missing' / 'candidate')

    def test_wrong_repository_root_is_rejected(self):
        with self.assertRaisesRegex(gate.RebuildError, 'repository root'):
            gate.rebuild(self.repo / '_scripts', self.target)
        self.assertFalse(self.target.exists())


if __name__ == '__main__':
    unittest.main()
