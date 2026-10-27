"""Professional presentation must not manufacture authority or rewrite history."""
import local_fonts_history
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import re
import shutil
import struct
import sys
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import identity
import presentation
import check_live
from test_site import Page

PROTECTED = json.loads((ROOT / '_tests/presentation-baseline.json').read_text())

class PresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.config = presentation.load(ROOT, cls.pages)

    def test_article_has_scope_disclosure_and_complete_routes(self):
        article = self.outputs[Path('notes/keep-the-judgment/index.html')]
        self.assertIn('Saturday-afternoon scenario is fictional', article)
        self.assertIn('not a report of measured results', article)
        self.assertIn('href="#about-this-essay"', article)
        self.assertIn('id="about-this-essay"', article)
        for name in ['index.html','notes/index.html','technology/index.html','about/index.html','bio/index.html','start-here/index.html']:
            self.assertIn('/notes/keep-the-judgment/', self.outputs[Path(name)])
        words = re.findall(r'\b[\w-]+\b', re.sub(r'<[^>]+>', ' ', (ROOT/'_source/notes/keep-the-judgment.html').read_text()))
        self.assertGreater(len(words), 1100)
        self.assertNotIn(chr(0x2014), article)

    def test_one_new_feed_item_with_stable_identity(self):
        items = ET.fromstring(self.outputs[Path('feed.xml')]).findall('./channel/item')
        self.assertEqual(len(items), 6)
        self.assertEqual(items[0].findtext('link'), 'https://nolankido.com/notes/keep-the-judgment/')
        self.assertEqual(items[0].findtext('guid'), items[0].findtext('link'))
        self.assertEqual(items[0].findtext('pubDate'), 'Sun, 11 Oct 2026 00:00:00 GMT')
        self.assertIn('/notes/keep-the-judgment/', self.outputs[Path('sitemap.xml')])

    def test_published_dates_not_curation_dates_on_cards(self):
        config = identity.load(ROOT, self.pages)
        by_path = {p['path']: p for p in self.pages}
        for item in config['selected']:
            fragment = identity.selected_reading({'selected':[item]}, self.pages)
            self.assertIn('datetime="'+by_path[item['path']]['date']+'"', fragment)
        fragment = presentation.publication({'date':'2026-10-05','updated':'2026-10-11'})
        self.assertIn('October 5, 2026', fragment)
        self.assertNotIn('October 11', fragment)
        self.assertEqual(presentation.publication({}), '')

    def test_notes_have_linked_byline_reading_time_and_disclosure(self):
        for page in self.pages:
            if page.get('note'):
                content = self.outputs[build.output_path(page['path'])]
                self.assertIn('<a href="/about/">Nolan Kido</a>', content)
                self.assertRegex(content, r'About [1-9][0-9]* min read')
                self.assertIn('AI-assisted essay', content)
                self.assertIn('Prepared with AI assistance.', content)
                self.assertIn('class="utility-writing" href="/notes/" aria-current="location"', content)
        self.assertIn('class="utility-writing" href="/notes/" aria-current="page"', self.outputs[Path('notes/index.html')])

    def test_every_page_has_one_valid_local_image_and_retains_metadata(self):
        for page in self.pages:
            with self.subTest(page=page['path']):
                content = self.outputs[build.output_path(page['path'])]
                tags=Page(content).tags('meta')
                values={a.get('name', a.get('property')):a.get('content') for a in tags}
                card=self.config['pages'].get(page['id'], self.config['default'])
                self.assertEqual(sum(a.get('property')=='og:image' for a in tags),1)
                self.assertEqual(values['og:image'], 'https://nolankido.com'+card['src'])
                self.assertEqual(values['twitter:image'],values['og:image'])
                self.assertEqual(values['og:image:width'],'1200')
                self.assertEqual(values['og:image:height'],'630')
                self.assertEqual(values['og:image:alt'],card['alt'])
                self.assertEqual(values['twitter:image:alt'],card['alt'])
                self.assertEqual(values['twitter:card'],'summary_large_image')
                self.assertEqual(values['og:title'],page['seo_title'])
                self.assertEqual(values['og:description'],page['description'])
                self.assertEqual(values['og:url'],'https://nolankido.com'+page['path'])
                self.assertIn('class="utility-writing"',content)

    def test_cards_are_exact_live_targets_and_png_sizes(self):
        targets=check_live.targets()
        for card in [self.config['default'],*self.config['pages'].values()]:
            raw=(ROOT/card['src'].lstrip('/')).read_bytes()
            self.assertEqual(struct.unpack('>II',raw[16:24]),(1200,630))
            self.assertLess(len(raw),25_000)
            self.assertEqual(targets[card['src']],(200,raw))
        self.assertIn('/notes/keep-the-judgment/', targets)

    def test_original_bodies_sensitive_boundaries_and_other_feeds_stay_fixed(self):
        for path, digest in PROTECTED.items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256(local_fonts_history.before(path,(ROOT/path).read_bytes())).hexdigest(),digest)
        article=self.outputs[Path('notes/keep-the-judgment/index.html')]
        for phrase in ['my clients','my patients','years of experience','guaranteed results','award-winning']:
            self.assertNotIn(phrase, article.lower())

    def validate_config(self, config, binary=None):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'_source').mkdir()
            shutil.copytree(ROOT/'assets/social',root/'assets/social')
            (root/'_source/presentation.json').write_text(json.dumps(config))
            if binary is not None:
                (root/'assets/social/nolan-kido.png').write_bytes(binary)
            return presentation.load(root,self.pages)

    def test_bad_card_config_is_rejected(self):
        for src in ['https://other.test/x.png','/assets/social/../../private.png','/assets/social/x.svg','//other.test/x.png']:
            config=deepcopy(self.config);config['default']['src']=src
            with self.subTest(src=src), self.assertRaises(ValueError):self.validate_config(config)
        config=deepcopy(self.config);config['pages']['not-a-real-page']=config['default']
        with self.assertRaises(ValueError):self.validate_config(config)
        config=deepcopy(self.config);config['default']['alt']=' '
        with self.assertRaises(ValueError):self.validate_config(config)
        for raw in [b'bad', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR', (ROOT/'assets/social/nolan-kido.png').read_bytes()[:16]+struct.pack('>II',3,4)+b'0'*40]:
            with self.assertRaises(ValueError):self.validate_config(self.config,raw)

    def test_card_alt_cannot_inject_metadata(self):
        config=deepcopy(self.config);config['default']['alt']='"><script>alert(1)</script>'
        # Home now has its own AI card. Exercise the default on a page that
        # actually uses it, so this remains an effective escaping check.
        fallback_id=next(page['id'] for page in self.pages if page['id'] not in config['pages'])
        output=presentation.metadata(config,{'id':fallback_id},'https://nolankido.com')
        self.assertNotIn('<script>',output)
        self.assertIn('&lt;script&gt;',output)
        self.assertIn('&quot;',output)

if __name__=='__main__':unittest.main()
