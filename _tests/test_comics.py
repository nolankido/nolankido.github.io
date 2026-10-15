"""Comic publication, readable alternatives, and exact predecessor protection."""
from hashlib import sha256
from pathlib import Path
import json
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import comics_history as history

class ComicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()

    def test_prior_content_remains_exact_and_unreviewed_mutations_remain_visible(self):
        frozen = history.change()
        self.assertEqual(frozen['base_commit'], 'c929afb071095d529842873bee6bba05e6060eac')
        for path, entry in frozen['paths'].items():
            raw = (ROOT / path).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), entry['new_sha256'], path)
            self.assertEqual(sha256(history.before(path, raw)).hexdigest(), entry['old_sha256'], path)
        path = 'poker/holdem-basics/index.html'
        raw = self.outputs[Path(path)]
        mutated = raw.replace('Two ways to win', 'Guaranteed profit')
        self.assertNotEqual(raw, mutated)
        self.assertEqual(history.before(path, mutated), mutated)

    def test_published_comic_is_reachable_and_feed_identity_is_unique(self):
        route = '/poker/comics/learn-no-limit-holdem/'
        for path in ['poker/index.html', 'poker/comics/index.html', 'poker/start-here/index.html', 'poker/find/index.html', 'find/index.html']:
            self.assertIn('href="'+route+'"', self.outputs[Path(path)], path)
        for name in ['poker/feed.xml', 'writing.xml']:
            items = ET.fromstring(self.outputs[Path(name)]).findall('./channel/item')
            self.assertEqual(sum(i.findtext('guid') == 'https://nolankido.com'+route for i in items), 1)
        html = self.outputs[build.output_path(route)]
        for text in ['id="text"', 'id="rules"', 'all-in raise', 'only two players seated', 'Artwork generated with Google Gemini', 'data-copy-page']:
            self.assertIn(text, html)
        self.assertNotIn(chr(8212), html)

    def test_local_artwork_and_styles_are_part_of_release_verification(self):
        targets = check_live.targets()
        for path in ['/assets/poker/comics/learn-no-limit-holdem.jpg', '/assets/poker-comics.css']:
            self.assertEqual(targets[path], (200, (ROOT / path.lstrip('/')).read_bytes()))
        self.assertEqual(sha256((ROOT/'assets/poker/comics/learn-no-limit-holdem.jpg').read_bytes()).hexdigest(), history.change()['new_files']['assets/poker/comics/learn-no-limit-holdem.jpg'])

if __name__ == '__main__': unittest.main()
