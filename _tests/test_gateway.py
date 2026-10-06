"""Technology-first hierarchy and small, honest subject destinations."""
from html.parser import HTMLParser
from pathlib import Path
import json
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live

class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.destinations = []
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'a' and 'destination' in values.get('class', '').split():
            self.destinations.append(values['href'])

class GatewayTests(unittest.TestCase):
    def test_three_real_destinations_in_reading_order(self):
        outputs = build.build_outputs()
        home = outputs[Path('index.html')]
        self.assertEqual(Links(home).destinations, ['/technology/', '/poker/', '/creative/'])
        self.assertIn('Technology, poker,<br>and creative work.', home)
        self.assertNotIn('destination-notes', home)
        for route in Links(home).destinations:
            self.assertIn(build.output_path(route), outputs)
            self.assertIn(route, check_live.targets())
        self.assertIn('/notes/', home)

    def test_shared_navigation_keeps_the_same_hierarchy(self):
        for path, html in build.build_outputs().items():
            if path.suffix != '.html':
                continue
            nav = html.split('<ul class="nav-links">')[1].split('</ul>')[0]
            with self.subTest(path=str(path)):
                self.assertLess(nav.index('/technology/'), nav.index('/poker/'))
                self.assertLess(nav.index('/poker/'), nav.index('/creative/'))
                self.assertIn('Creative Work</a>', nav)
                self.assertNotIn('/notes/', nav)
        for section in ['technology', 'creative']:
            self.assertIn('href="/' + section + '/" aria-current="page"', build.build_outputs()[Path(section + '/index.html')])

    def test_new_overviews_describe_actual_scope(self):
        outputs = build.build_outputs()
        technology = outputs[Path('technology/index.html')]
        creative = outputs[Path('creative/index.html')]
        self.assertIn('not yet a project portfolio', technology)
        self.assertIn('/notes/trustworthy-tools/', technology)
        self.assertIn('/resources/#tool-trust-check', technology)
        self.assertIn('not yet a gallery', creative)
        self.assertIn('/notes/generous-explanations/', creative)
        self.assertIn('/notes/finishing-is-a-decision/', creative)
        for page in [technology, creative]:
            for unsupported in ['<iframe', 'coming soon', 'Join the waitlist', '<form']:
                self.assertNotIn(unsupported, page)
        notes = [p for p in json.loads((ROOT / '_source/pages.json').read_text()) if p.get('note')]
        self.assertEqual(len(notes), 5)

if __name__ == '__main__':
    unittest.main(verbosity=2)
