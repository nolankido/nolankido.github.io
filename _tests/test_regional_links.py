"""Region-dependent external sources get visible, truthful routing cautions."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_resources
import regional_link_history as history

EXPECTED = {
    'stars-poker-rules', 'holdem-rules', 'hand-rankings', 'poker-glossary',
    'stars-learn', 'spr', 'tournament-types', 'omaha-rules', 'razz-rules',
    'horse-rules', 'omaha-eight-rules', 'stud-eight-rules',
    'deuce-seven-rules', 'eight-game-rules', 'five-card-omaha-rules',
    'six-plus-rules', 'stars-rake', 'stars-tool-policy'
}

class RegionalLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = poker_resources.load(ROOT)
        cls.page = build.build_outputs()[Path('poker/resources/index.html')]

    def test_exact_18_website_links_without_hijacking_live_operator_pages(self):
        from urllib.parse import urlsplit
        selected = {e['id'] for e in self.entries
                    if urlsplit(e['url']).hostname in {'pokerstars.com', 'www.pokerstars.com'}}
        self.assertEqual(selected, EXPECTED)
        self.assertEqual(len(self.entries), 146)
        for entry in self.entries:
            card = poker_resources.card(entry)
            count = card.count('class="small-copy resource-caution resource-region"')
            self.assertEqual(count, int(entry['id'] in EXPECTED), entry['id'])
            self.assertEqual(card.count('rel="external"'), 1)
            self.assertEqual(card.count('data-resource-jump'), 1)
            self.assertIn('href="' + entry['url'] + '"', card)
            self.assertIn(entry['reviewed_on'], card)
            self.assertEqual('pokerstarslive.com' in entry['url'] and count > 0, False)

    def test_cautions_and_local_fallbacks_remain_in_static_html(self):
        source = (ROOT / '_source/poker/resources.html').read_text()
        self.assertEqual(source.count('id="regional-operator-links"'), 1)
        self.assertEqual(self.page.count('id="regional-operator-links"'), 1)
        self.assertEqual(self.page.count('class="small-copy resource-caution resource-region"'), 18)
        for phrase in ('different destinations by region', 'does not verify the specific policy',
                       'check its publisher and heading', 'no alternate operator is endorsed'):
            self.assertIn(phrase, self.page)
        for route in ('/poker/hand-rankings/', '/poker/omaha-and-mixed-games/',
                      '/poker/poker-rules-and-fair-play/'):
            self.assertIn('href="' + route + '"', source)
            self.assertIn('href="' + route + '"', self.page)
        self.assertNotIn('fanduel', source.lower())
        self.assertNotIn('fanduel', poker_resources.regional_link_notice(self.entries[0]).lower())
        self.assertNotIn('<script', source)
        self.assertNotIn('<form', source)

    def test_exact_parent_reconstruction_rejects_unrecognized_changes(self):
        self.assertEqual(set(history.change()['paths']), history.PATHS)
        for name, item in history.change()['paths'].items():
            raw = (ROOT / name).read_bytes()
            with self.subTest(name=name):
                self.assertEqual(sha256(raw).hexdigest(), item['new_sha256'])
                old = history.before(name, raw)
                self.assertEqual(sha256(old).hexdigest(), item['old_sha256'])
                self.assertEqual(history.before(Path(name), raw.decode()).encode(), old)
                self.assertEqual(history.before(name, old), old)
                for altered in (raw + b'!', b'!' + raw, raw[1:]):
                    self.assertEqual(history.before(name, altered), altered)

    def test_corrupt_parent_fingerprint_and_insertion_fail_closed(self):
        name = 'poker/resources/index.html'
        raw = (ROOT / name).read_bytes()
        for fault in ('old_sha256', 'edits'):
            bad = deepcopy(history.change())
            if fault == 'old_sha256':
                bad['paths'][name][fault] = '0' * 64
            else:
                bad['paths'][name]['edits'][1]['count'] = 17
            with patch.object(history, 'change', return_value=bad):
                with self.assertRaises(ValueError):
                    history.before(name, raw)
        self.assertEqual(history.before('unrelated.html', b'stable'), b'stable')

if __name__ == '__main__':
    unittest.main()
