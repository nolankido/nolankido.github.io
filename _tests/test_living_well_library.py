"""Expanded library, preserved reader links, and approved public-introduction contracts."""
from copy import deepcopy
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import check_living_well_links as link_check
import living_well as lw
import living_well_resources as library

OLD_IDS = {'on-being','pluralism','closer-to-truth','ucla-mindful','greater-good','plum-village',
           'how-ai-works','openai-academy','claude-academy','merlin','seek','libby','storycorps',
           'personal-archiving','be-my-eyes','openlearn','evolution-of-trust','poetry-unbound'}

class LibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = library.load(ROOT)
        cls.outputs = build.build_outputs()
        cls.readings = {e['slug']: e for e in lw.load(ROOT)}
        cls.hub = cls.outputs[Path('living-well/free-resources/index.html')]

    def test_twelve_distinct_collection_pages_with_complete_context(self):
        self.assertEqual(len(library.manifest(ROOT)), 12)
        self.assertEqual(len(lw.manifest(ROOT)), 53)
        live = check_live.targets()
        for shelf in self.data['shelves']:
            with self.subTest(shelf=shelf['id']):
                route = library.collection_route(shelf['id'])
                page = self.outputs[build.output_path(route)]
                self.assertIn(route, live)
                self.assertIn(route, self.outputs[Path('sitemap.xml')])
                self.assertIn('href="' + route + '"', self.hub)
                self.assertIn(escape(shelf['orientation']), page)
                self.assertIn(escape(shelf['approach']), page)
                self.assertIn('id="' + shelf['start_id'] + '"', page)
                for companion in shelf['companions']:
                    self.assertIn(companion, self.readings)
                    self.assertIn('href="/living-well/' + companion + '/"', page)
                schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S).group(1))
                self.assertEqual(schema['@type'], 'CollectionPage')
                self.assertNotIn('datePublished', schema)
                self.assertIn('href="/living-well/free-resources/" aria-current="location"', page)

    def test_every_selection_has_one_full_home_and_a_stable_index_anchor(self):
        ids = {e['id'] for e in self.data['resources']}
        self.assertTrue(OLD_IDS <= ids)
        self.assertEqual(len(ids), 66)
        all_details = ''.join(self.outputs[build.output_path(library.collection_route(s['id']))] for s in self.data['shelves'])
        for e in self.data['resources']:
            with self.subTest(resource=e['id']):
                self.assertEqual(all_details.count('class="lw-card lw-resource" id="' + e['id'] + '"'), 1)
                self.assertEqual(self.hub.count('id="' + e['id'] + '"'), 1)
                page = self.outputs[build.output_path(library.collection_route(e['shelf']))]
                self.assertIn(escape(e['requirements']), page)
                self.assertIn(escape(e['perspective']), page)
                self.assertIn(escape(e['limit']), page)
                self.assertIn(escape(e['review_scope']), page)
                self.assertIn('href="' + escape(e['entry_url'], quote=True) + '"', page)
                self.assertIn('href="' + library.collection_route(e['shelf']) + '#' + e['id'] + '"', self.hub)

    def test_reader_choice_does_not_add_tracking_or_implicit_affiliation(self):
        self.assertIn('not a claim of affiliation, personal use', self.hub)
        self.assertIn('There are no affiliate links or paid placements', self.hub)
        for p in library.manifest(ROOT):
            body = self.outputs[build.output_path(p['path'])]
            self.assertNotRegex(body, r'<(?:form|input|iframe|textarea)\b')
            scripts = re.findall(r'<script[^>]+src="([^"]+)"', body)
            self.assertEqual(scripts, ['https://cloud.umami.is/script.js'])
            self.assertNotIn('utm_', body)
            self.assertNotIn(chr(0x2014), body)
        self.assertEqual(len(self.readings), 26)
        self.assertEqual(sum(e['kind'] == 'experiment' for e in self.readings.values()), 3)

    def test_invalid_library_context_is_rejected(self):
        for change in [lambda d: d['shelves'][0].update(group='absent'),
                       lambda d: d['shelves'][0].update(orientation=''),
                       lambda d: d['shelves'][0].update(companions=['bad/route', 'bad']),
                       lambda d: d['resources'][0].update(perspective=''),
                       lambda d: d['groups'][0].update(title='')]:
            data = deepcopy(self.data); change(data)
            with TemporaryDirectory() as td:
                path = Path(td) / '_source/living-well/resources.json'
                path.parent.mkdir(parents=True); path.write_text(json.dumps(data))
                with self.assertRaises(ValueError): library.load(Path(td))
        for invalid in ('../contact', '', 'x?y', 'a/b'):
            with self.assertRaises(ValueError): library.collection_route(invalid)

    def test_public_introductions_include_living_well_without_new_private_fields(self):
        site = json.loads((ROOT / '_source/site.json').read_text())
        self.assertEqual(set(site), {'name','url','year','tagline','intro','bio_short','bio_long','form_action','turnstile_sitekey'})
        self.assertEqual(site['name'], 'Nolan Kido')
        self.assertEqual(site['url'], 'https://nolankido.com')
        self.assertEqual(site['form_action'], 'https://submit-form.com/uPlTgRTAR')
        self.assertEqual(site['turnstile_sitekey'], '0x4AAAAAAFI2X8NC1cauc_zz')
        for key in ('tagline', 'bio_long'):
            self.assertIn('Living Well', site[key])
        for route in ['about/index.html', 'bio/index.html']:
            self.assertIn('Living Well', self.outputs[Path(route)])
        for phrase in ('spiritual teacher', 'certified', 'my patients', 'clients include', 'award-winning', 'my daily meditation'):
            self.assertNotIn(phrase, (site['bio_short'] + site['bio_long']).lower())
        self.assertIn('/living-well/free-resources/', self.outputs[Path('about/index.html')])

    def test_link_diagnostics_do_not_equate_access_with_http_success(self):
        self.assertEqual(link_check.classify_status(200), 'responded')
        self.assertEqual(link_check.classify_status(404), 'not-found')
        self.assertEqual(link_check.classify_status(403), 'restricted-or-rate-limited')
        self.assertEqual(link_check.classify_status(429), 'restricted-or-rate-limited')
        self.assertEqual(link_check.classify_status(500), 'needs-review')

    def test_original_global_and_contact_assets_stay_fixed(self):
        protected = {
            'assets/contact.js':'65b6fc99c23c947f4bcc9b427bc04b08dfabd6333c8c26e9ad6c506adc370858',
            'styles.css':'44be94f4cc9dc8ff7af79d975ceae280ae2c01d7ef755db28effbeb6fbfeb4ef',
            'assets/site.css':'784f0d0fb3faeefc953712470a5b86dde775e9c9991e7b22fbc0241ccc69acf6',
            'assets/hubs.css':'51ecd02a1c5b66ddd80c08f1b61a128827d45854c4d5ad4d912bc5d881204800',
            '_source/poker/catalog.json':'7c1051f6e2bc3943b7c1dbe4da229694455681b8875a346c99279e555edb733f'}
        for path, expected in protected.items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), expected, path)

if __name__ == '__main__':
    unittest.main(verbosity=2)
