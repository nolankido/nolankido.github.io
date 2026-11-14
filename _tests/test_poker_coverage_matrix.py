"""The Poker authority sprint inventory must stay derived from published sources."""

from pathlib import Path
import json
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import poker_coverage_matrix


class CoverageMatrixTests(unittest.TestCase):
    def test_committed_matrix_is_current(self):
        generated = poker_coverage_matrix.render(poker_coverage_matrix.inventory(ROOT))
        self.assertEqual(generated,
                         poker_coverage_matrix.REPORT.read_text(encoding='utf-8'))

    def fixture(self, destination: Path) -> Path:
        source = destination / '_source/poker'
        finder = destination / 'poker/find'
        source.mkdir(parents=True)
        finder.mkdir(parents=True)
        for name in ('library', 'topics', 'resources', 'collections'):
            shutil.copyfile(ROOT / '_source/poker' / f'{name}.json', source / f'{name}.json')
        shutil.copyfile(ROOT / 'poker/find/index.html', finder / 'index.html')
        return destination

    def test_missing_primary_guide_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(Path(directory))
            path = root / '_source/poker/topics.json'
            data = json.loads(path.read_text(encoding='utf-8'))
            data['entries'][0]['primary_guides'].pop()
            path.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Guides without a primary topic'):
                poker_coverage_matrix.inventory(root)

    def test_finder_missing_external_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(Path(directory))
            path = root / 'poker/find/index.html'
            body = path.read_text(encoding='utf-8')
            self.assertIn('data-id="external-tda-rules"', body)
            path.write_text(body.replace('data-id="external-tda-rules"',
                                         'data-id="unmatched-card"', 1), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Generated Poker Finder omissions'):
                poker_coverage_matrix.inventory(root)


if __name__ == '__main__':
    unittest.main()
