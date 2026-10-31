"""Personal introduction and curated routes must stay truthful, usable and connected."""
import copy
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import identity
import check_live

class IdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.config = identity.load(ROOT, cls.pages)
        cls.outputs = build.build_outputs()

    def test_identity_precedes_reading_and_libraries(self):
        home = self.outputs[Path('index.html')]
        self.assertLess(home.index('home-title'), home.index('selected-reading-title'))
        self.assertLess(home.index('selected-reading-title'), home.index('destinations-title'))
        self.assertIn('<p class="hero-copy brand-statement">AI Works Human Decides</p>', home)
        self.assertIn('I also build software tools and play tournament poker.', home)
        self.assertIn('href="/about/">Meet Nolan', home)
        self.assertIn('href="/technology/#ai-works-human-decides">Practical AI in real life', home)
        self.assertIn('href="/technology/#technology-projects">Technology projects', home)
        self.assertIn('href="/poker/#watch">Poker with Nolan', home)
        self.assertIn('Food', self.outputs[Path('about/index.html')])

    def test_practical_ai_positioning_is_public_and_matches_machine_metadata(self):
        for route in ['index.html', 'about/index.html', 'technology/index.html']:
            content = self.outputs[Path(route)]
            self.assertIn('AI Works Human Decides', content)
            self.assertIn('Nolan Kido', content)
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', content).group(1))
            self.assertIn('AI Works Human Decides', schema['name'])
            self.assertIn('AI Works Human Decides', schema['description'])
            self.assertNotIn('Hawaii Dental Clinic and Affiliates', content)
        method = self.outputs[Path('technology/index.html')]
        self.assertIn('id="ai-works-human-decides"', method)
        for path in ['/technology/should-i-use-ai/', '/technology/task-brief/',
                     '/technology/check-ai-answers/', '/technology/ai-time-savings/',
                     '/technology/checking-ai-website-changes/']:
            self.assertIn('href="' + path + '"', method)
        self.assertIn('Human Decides', self.outputs[Path('card/index.html')])
        self.assertIn('AI Works Human Decides', self.outputs[Path('bio/index.html')])

    def test_curated_entries_keep_canonical_titles_and_status(self):
        by_path = {p['path']: p for p in self.pages}
        for relative in ['start-here/index.html']:
            content = self.outputs[Path(relative)]
            self.assertEqual(content.count('class="identity-reading"'), 3)
            for item in self.config['selected']:
                self.assertIn(item['path'], content)
                self.assertIn(build.text(by_path[item['path']]['title']), content)
            self.assertIn('Fictional hand', content)
            self.assertNotIn('Proposed experiment:', content)
        start = self.outputs[Path('start-here/index.html')]
        self.assertIn('plans, not completed results', start)
        self.assertIn('/start-here/', check_live.targets())

    def test_every_page_can_return_to_the_personal_introduction(self):
        for path, content in self.outputs.items():
            if path.suffix == '.html':
                with self.subTest(path=path):
                    self.assertIn('class="utility-start" href="/start-here/"', content)
                    self.assertIn('/start-here/#reading-this-site', content)

    def test_profile_schema_does_not_invent_credentials(self):
        for relative in ['index.html', 'about/index.html']:
            content = self.outputs[Path(relative)]
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', content).group(1))
            person = schema['mainEntity']
            self.assertEqual(person['@id'], 'https://nolankido.com/about/#nolan-kido')
            self.assertEqual(set(person), {'@type','@id','name','url','description','sameAs'})
            self.assertEqual(person['sameAs'], ['https://github.com/nolankido', 'https://dev.to/kidon'])
            if relative.startswith('about'):
                self.assertEqual(schema['@type'], 'ProfilePage')

    def test_rejects_missing_or_duplicate_curated_routes(self):
        for change in ['missing', 'duplicate']:
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp); (root / '_source').mkdir()
                config = copy.deepcopy(self.config)
                config['selected'][0]['path'] = '/not-published/' if change == 'missing' else config['selected'][1]['path']
                (root / '_source/identity.json').write_text(json.dumps(config))
                with self.assertRaises(ValueError):
                    identity.load(root, self.pages)

if __name__ == '__main__':
    unittest.main()
