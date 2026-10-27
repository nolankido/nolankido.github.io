"""Search arrivals can find each existing part of the Technology hub natively."""
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import beginner_history
import brand_positioning_history as brand_history
import build
import technology_jumps_history as history
import study_titles_history
import turn04_public_source_history
from test_site import Page


class TechnologyJumpsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = {p: study_titles_history.before(p, turn04_public_source_history.before(p, brand_history.before(p, data)))
                       for p, data in build.build_outputs().items()}
        cls.baseline = json.loads((ROOT / '_tests/technology-jumps-baseline.json').read_text())

    def test_only_the_existing_technology_opening_navigation_changes(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        b = self.baseline
        self.assertEqual(sha256(json.dumps(study_titles_history.pages(beginner_history.pages(brand_history.pages(build.public_pages()))), sort_keys=True, ensure_ascii=False).encode()).hexdigest(), b['pages_sha256'])
        self.assertEqual((len(b['outputs']), len(b['files'])), (198, 343))
        # The later, separately tested profile graph did not exist in this
        # frozen release. Keep it published without retroactively adding it
        # to the historical Technology navigation inventory.
        historical_outputs.pop(Path('assets/nolan-kido-identity.jsonld'), None)
        self.assertEqual(set(map(str, historical_outputs)), set(b['outputs']))
        changed = []
        for path, expected in b['outputs'].items():
            raw = historical_outputs[Path(path)]
            if sha256(raw.encode()).hexdigest() != expected:
                changed.append(path)
            self.assertEqual(sha256(history.before(path, raw).encode()).hexdigest(), expected, path)
        self.assertEqual(changed, ['technology/index.html'])
        tracked = subprocess.check_output(['git', 'ls-files', '_source', 'assets', 'downloads'], cwd=ROOT).decode().splitlines()
        files = beginner_history.files(set(tracked) - {'_source/person-schema.jsonld', 'assets/nolan-kido-identity.jsonld'})
        self.assertEqual(files, set(b['files']))
        changed = []
        for path, expected in b['files'].items():
            raw = study_titles_history.before(path, brand_history.before(path, (ROOT / path).read_bytes()))
            if sha256(raw).hexdigest() != expected:
                changed.append(path)
            self.assertEqual(sha256(history.before(path, raw)).hexdigest(), expected, path)
        self.assertEqual(changed, ['_source/technology/home.html'])

    def test_four_native_links_cover_the_actual_sections_in_reading_order(self):
        raw = self.outputs[Path('technology/index.html')]
        block = re.search(r'<nav class="link-row technology-jumps".*?</nav>', raw)[0]
        doc = Page(block)
        self.assertEqual(doc.tags('nav')[0]['aria-label'], 'On this Technology page')
        links = doc.tags('a')
        targets = ['practical-ai-path', 'working-examples', 'technology-path', 'technology-reading']
        self.assertEqual([a['href'] for a in links], ['#' + target for target in targets])
        self.assertTrue(all(set(a) == {'href', 'class'} for a in links))
        self.assertFalse(doc.tags('button') or doc.tags('script'))
        self.assertEqual(links[0]['class'], 'button')
        self.assertTrue(all(a.get('aria-hidden') == 'true' for a in doc.tags('span')))
        positions = [raw.index('id="' + target + '"') for target in targets]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(raw.index(block), min(positions))
        for target in targets:
            self.assertEqual(raw.count('id="' + target + '"'), 1)
        self.assertIn('<a href="/contact/">Talk technology</a>', raw)
        for route in ['/technology/should-i-use-ai/', '/technology/task-brief/',
                      '/technology/check-ai-answers/', '/technology/ai-time-savings/']:
            self.assertIn('href="' + route + '"', raw)
        self.assertNotIn('\u2014', block)
        old = Page(history.change()['old'])
        self.assertNotIn('#practical-ai-path', [a['href'] for a in old.tags('a')])
        self.assertNotIn('#technology-reading', [a['href'] for a in old.tags('a')])

    def test_frozen_adapter_keeps_unreviewed_navigation_and_copy_changes_detectable(self):
        for path in ['_source/technology/home.html', 'technology/index.html']:
            raw = (ROOT / path).read_text()
            for old, new in [('Follow the four-step workflow', 'A guaranteed result'),
                             ('href="#practical-ai-path"', 'href="https://other.example/"'),
                             ('Useful AI starts with a life', 'An unapproved biography'),
                             ('href="/contact/">Talk technology', 'href="/missing/">Talk technology')]:
                changed = raw.replace(old, new, 1)
                self.assertNotEqual(changed, raw)
                self.assertNotEqual(history.before(path, changed), history.before(path, raw))
        block = history.change()['new']
        self.assertEqual(history.before('about/index.html', block), block)
        self.assertEqual(history.before('assets/example.woff2', b'\xff\x00'), b'\xff\x00')
        self.assertEqual(history.before('technology/index.html', block + block), history.change()['old'] + block)


if __name__ == '__main__':
    unittest.main()
