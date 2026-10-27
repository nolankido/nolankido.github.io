"""Per-page brand sharing is relevant, reversible, and mutation-detecting."""
from hashlib import sha256
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import build
import brand_positioning_history
import presentation
import scoped_share_history as history
from test_site import Page


class ScopedShareHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = history.change()
        cls.outputs = build.build_outputs()

    def test_all_87_scoped_changes_reverse_exactly_and_only_they_reverse(self):
        self.assertEqual(len(self.record['paths']), 87)
        self.assertEqual(sum(v['mode'] == 'social-metadata' for v in self.record['paths'].values()), 84)
        for path, item in self.record['paths'].items():
            with self.subTest(path=path):
                current = (ROOT / path).read_bytes()
                if sha256(current).hexdigest() != item['current_sha256']:
                    # A newer release is not an error in this archived record.
                    self.assertEqual(history.before(path, current), current)
                    continue
                previous = history.before(path, current)
                self.assertEqual(sha256(previous).hexdigest(), item['parent_sha256'])
                self.assertEqual(history.before(path, previous), previous)
                for edited in (current + b'UNREVIEWED', b'UNREVIEWED' + current, current[1:]):
                    self.assertEqual(history.before(path, edited), edited)
        self.assertEqual(history.before('unrelated.json', b'untouched'), b'untouched')

    def test_brand_history_rewinds_the_two_intentional_releases_in_order(self):
        original = brand_positioning_history.change()
        for path, item in self.record['paths'].items():
            if path not in original['paths']:
                continue
            current = (ROOT / path).read_bytes()
            if sha256(current).hexdigest() == item['current_sha256']:
                restored = brand_positioning_history.before(path, current)
                self.assertEqual(sha256(restored).hexdigest(), original['paths'][path]['old_sha256'])

    def test_relevant_entry_pages_have_ai_card_and_other_topics_keep_general_card(self):
        general = 'https://nolankido.com/assets/social/nolan-kido.png'
        ai = 'https://nolankido.com/assets/social/nolan-kido-ai.png'
        general_alt = 'Nolan Kido. Build useful things. Make room for a good life. nolankido.com.'
        ai_alt = 'Nolan Kido. AI Works Human Decides. Practical AI for real life. nolankido.com.'
        pages = build.public_pages()
        config = presentation.load(ROOT, pages)
        branded_pages = {page['id'] for page in pages
                         if config['pages'].get(page['id'], config['default'])['src'] == '/assets/social/nolan-kido-ai.png'}
        self.assertEqual(branded_pages, {'home', 'about'})

        def social(route):
            attrs = Page(self.outputs[Path(route)]).tags('meta')
            return {item.get('name', item.get('property')): item['content']
                    for item in attrs if 'content' in item}

        for route in ['index.html', 'about/index.html']:
            with self.subTest(route=route):
                meta = social(route)
                self.assertEqual(meta['og:image'], ai)
                self.assertEqual(meta['twitter:image'], ai)
                self.assertEqual(meta['og:image:alt'], ai_alt)
                self.assertEqual(meta['twitter:image:alt'], ai_alt)
        for route in ['poker/study/index.html', 'poker/resources/index.html',
                      'living-well/topics/everyday-ai/index.html', 'privacy/index.html']:
            with self.subTest(route=route):
                meta = social(route)
                self.assertEqual(meta['og:image'], general)
                self.assertEqual(meta['twitter:image'], general)
                self.assertEqual(meta['og:image:alt'], general_alt)
                self.assertEqual(meta['twitter:image:alt'], general_alt)
        technology = social('technology/index.html')
        self.assertEqual(technology['og:image'], 'https://nolankido.com/assets/social/practical-ai.png')

    def test_both_card_assets_are_exact_and_reviewable_without_photo_uploads(self):
        self.assertEqual(sha256((ROOT / 'assets/social/nolan-kido.png').read_bytes()).hexdigest(),
                         '1b49328d0c9dbdcea8037c3866cb9d3a4ce1574debd86031b1792f29033cbe7a')
        new = self.record['new_asset']
        self.assertEqual(new['path'], 'assets/social/nolan-kido-ai.png')
        self.assertEqual(sha256((ROOT / new['path']).read_bytes()).hexdigest(), new['sha256'])
        self.assertNotIn('assets/nolan-kido-headshot.jpg', self.record['paths'])
        self.assertNotIn('assets/nolan-kido-headshot-square.jpg', self.record['paths'])


if __name__ == '__main__':
    unittest.main()
