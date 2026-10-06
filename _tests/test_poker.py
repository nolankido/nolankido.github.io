"""Gateway, poker navigation, public boundaries, and worked-hand regressions."""
import hashlib
import json
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
from poker_navigation import section_navigation

class PokerTests(unittest.TestCase):
    def test_poker_is_local_and_complete(self):
        outputs = build.build_outputs()
        for path in ['poker/index.html', 'poker/reviewing-a-hand/index.html']:
            page = outputs[Path(path)]
            self.assertIn('aria-label="Poker section"', page)
            self.assertIn('/poker/reviewing-a-hand/', page)
            self.assertIn('/downloads/poker-hand-review.md', page)
            for forbidden in ['<iframe', 'youtube.com', 'youtu.be', 'coming soon', 'solverPoker', 'OverlayPoker', 'Thunder Valley', 'mailto:']:
                self.assertNotIn(forbidden, page)
        self.assertNotIn('aria-label="Poker section"', outputs[Path('index.html')])
        self.assertEqual(section_navigation({'path':'/notes/'}), '')
        self.assertIn('href="/poker/" aria-current="page"', outputs[Path('poker/index.html')])
        self.assertIn('href="/poker/" aria-current="location"', outputs[Path('poker/reviewing-a-hand/index.html')])

    def test_guide_is_honest_and_hand_arithmetic_matches(self):
        text = build.build_outputs()[Path('poker/reviewing-a-hand/index.html')]
        self.assertIn('fictional', text)
        self.assertIn('Prepared with AI assistance.', text)
        self.assertIn('Use it after play.', text)
        self.assertEqual(Fraction('2.5') * 2 + Fraction('0.5'), Fraction('5.5'))
        self.assertEqual(Fraction('5.5') + 2 + 7, Fraction('14.5'))
        self.assertEqual(7 - 2, 5)
        for phrase in ['5.5 BB: 2.5 + 2.5 + 0.5', '14.5 BB: 5.5 + 2 + 7', '5 BB more to call, not 7 BB', '30 big blinds effective']:
            self.assertIn(phrase, text)
        self.assertNotIn('<form', text)
        sheet = (ROOT / 'downloads/poker-hand-review.md').read_text()
        self.assertIn('What you thought at the table', sheet)
        self.assertIn('Result, recorded separately', sheet)

    def test_new_assets_have_content_versions_and_live_checks(self):
        version = hashlib.sha256((ROOT / 'assets/hubs.css').read_bytes()).hexdigest()[:12]
        for path, content in build.build_outputs().items():
            if path.suffix == '.html':
                self.assertIn('/assets/hubs.css?v=' + version, content)
        targets = check_live.targets()
        for route in ['/poker/', '/poker/reviewing-a-hand/', '/assets/hubs.css', '/downloads/poker-hand-review.md']:
            self.assertIn(route, targets)

    def test_general_notes_and_their_dates_are_preserved(self):
        pages = json.loads((ROOT / '_source/pages.json').read_text())
        notes = [p for p in pages if p.get('note')]
        self.assertEqual(len(notes), 5)
        self.assertTrue(all(p['path'].startswith('/notes/') for p in notes))
        self.assertTrue(all(p['date'] == '2026-10-05' for p in notes))
        self.assertTrue(all(not p.get('note') for p in pages if p['path'].startswith('/poker/')))

if __name__ == '__main__':
    unittest.main(verbosity=2)
