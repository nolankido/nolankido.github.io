"""Turn 23: branded NolanPoker/AI identity answer with bounded evidence routes."""

from html.parser import HTMLParser
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import public_identity

PERSON = 'https://nolankido.com/about/#nolan-kido'
ABOUT = 'https://nolankido.com/about/'
CASE = 'https://nolankido.com/technology/ai-poker-video-evidence/'
ANCHOR = 'nolanpoker-ai-link'
DEST = '/about/#' + ANCHOR
YOUTUBE = 'https://www.youtube.com/@NolanPoker'
LINKS = (
    YOUTUBE,
    '/poker/nolan-kido/',
    '/poker/episodes/portland-meadows-ep1/#hand-64o-record',
    '/poker/episodes/portland-meadows-ep1/#hand-77-record',
    '/technology/ai-poker-video-evidence/#poker-ai-draft',
    '/downloads/portland-meadows-ep1-scene-claims.json',
    '/downloads/poker-vlog-fact-gate.py',
)
BOUNDS = (
    'Is NolanPoker the same Nolan Kido who writes about practical AI?',
    '<strong>Short answer:</strong> Yes.',
    "I'm Nolan Kido, and I publish first-person tournament videos",
    'One documented editorial exercise connects those interests',
    'draft captions are not verified as part of a released video',
    'A result listing can establish a finish, not the accuracy of every narrated hand',
    'not verified solver findings or a checked transcript of the current upload',
    'The checker does not inspect video frames or approve a publication',
    'that an AI draft was used in the current video',
    'that a tournament play was solver-approved',
    'that a product achieved a measured business result',
    'that I hold an official tournament-creator credential',
)


class Nodes(HTMLParser):
    def __init__(self, value):
        super().__init__()
        self.ids = []
        self.links = []
        self.feed(value)

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get('id'):
            self.ids.append(data['id'])
        if tag == 'a':
            self.links.append(data.get('href', ''))


def bridge_body(value):
    pattern = r'<section aria-labelledby="' + ANCHOR + r'">(.*?)</section>'
    match = re.search(pattern, value, re.S)
    return match.group(1) if match else ''


def bridge_errors(value):
    body = bridge_body(value)
    if not body:
        return ['missing author bridge']
    errors = []
    links = Nodes(body).links
    for target in LINKS:
        if links.count(target) != 1:
            errors.append('broken or duplicated evidence link: ' + target)
    for phrase in BOUNDS:
        if phrase not in body:
            errors.append('missing or inflated claim: ' + phrase)
    if '\u2014' in body:
        errors.append('em dash in new copy')
    return errors


def schema(value):
    records = re.findall(r'<script type="application/ld\+json">(.*?)</script>', value, re.S)
    if len(records) != 1:
        raise AssertionError('expected one JSON-LD record')
    return json.loads(records[0])


class NolanPokerAiIdentityBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '_source/about.html').read_text(encoding='utf-8')
        cls.public = (ROOT / 'about/index.html').read_text(encoding='utf-8')
        cls.manifest = {record['path']: record for record in json.loads(
            (ROOT / '_source/pages.json').read_text(encoding='utf-8'))}

    def test_single_branded_answer_and_old_about_landmarks(self):
        for value in (self.source, self.public):
            with self.subTest(generated=value is self.public):
                self.assertEqual(bridge_errors(value), [])
                nodes = Nodes(value)
                self.assertEqual(nodes.ids.count(ANCHOR), 1)
                self.assertEqual(nodes.links.count('#' + ANCHOR), 1)
                self.assertLess(value.index('id="who-is-nolan-kido"'),
                                value.index('id="' + ANCHOR + '"'))
                self.assertLess(value.index('id="' + ANCHOR + '"'),
                                value.index('id="about-evidence-title"'))
                for original in ('who-is-nolan-kido', 'about-evidence-title',
                                 'what-matters-in-the-work', 'try-the-work',
                                 'public-work-elsewhere'):
                    self.assertEqual(nodes.ids.count(original), 1, original)

    def test_topic_entrypoints_and_source_claim_boundaries(self):
        for relative in ('_source/poker/home.html', 'poker/index.html',
                         '_source/technology/ai-poker-video-evidence.html',
                         'technology/ai-poker-video-evidence/index.html'):
            with self.subTest(path=relative):
                self.assertEqual(Nodes((ROOT / relative).read_text()).links.count(DEST), 1)
        source = (ROOT / '_source/technology/ai-poker-video-evidence.html').read_text()
        self.assertIn('This proposed editorial workflow does not establish which captions', source)
        self.assertEqual(source.count('data-poker-ai-caption='), 3)
        record = json.loads((ROOT / 'downloads/portland-meadows-ep1-scene-claims.json').read_text())
        for key in ('human_release_approval', 'current_public_cut_graphics_checked',
                    'current_public_cut_timestamps_checked'):
            self.assertIs(record[key], False)

    def test_native_anchor_is_visible_with_keyboard_and_small_screen_offset(self):
        css = (ROOT / 'assets/about-reader.css').read_bytes()
        self.assertIn('.page-about #' + ANCHOR + ':target {', css.decode('utf-8'))
        self.assertIn('outline: 2px solid var(--red);', css.decode('utf-8'))
        self.assertIn('.page-about h2[id] { scroll-margin-top: 7rem; }', css.decode('utf-8'))
        self.assertIn('/assets/about-reader.css?v=' + sha256(css).hexdigest()[:12], self.public)

    def test_canonical_dates_person_and_existing_channel_identity(self):
        self.assertEqual(self.manifest['/about/']['updated'], '2026-11-19')
        self.assertEqual(self.manifest['/poker/']['updated'], '2026-11-19')
        self.assertEqual(self.manifest['/technology/ai-poker-video-evidence/']['date'], '2026-11-04')
        self.assertEqual(self.manifest['/technology/ai-poker-video-evidence/']['updated'], '2026-11-19')
        about = schema(self.public)
        self.assertEqual(about['@type'], 'ProfilePage')
        self.assertEqual(about['url'], ABOUT)
        self.assertEqual(about['mainEntity']['@id'], PERSON)
        self.assertEqual(about['mainEntity']['sameAs'], public_identity.same_as())
        self.assertIn(YOUTUBE, about['mainEntity']['sameAs'])
        case_html = (ROOT / 'technology/ai-poker-video-evidence/index.html').read_text()
        article = schema(case_html)
        self.assertEqual(article['@type'], 'Article')
        self.assertEqual(article['datePublished'], '2026-11-04')
        self.assertEqual(article['dateModified'], '2026-11-19')
        self.assertEqual(article['author']['@id'], PERSON)
        self.assertNotIn('FAQPage', (about['@type'], article['@type']))
        for url, html in ((ABOUT, self.public), (CASE, case_html)):
            self.assertIn('<link rel="canonical" href="' + url + '">', html)
        sitemap = ET.fromstring((ROOT / 'sitemap.xml').read_text())
        for url in (ABOUT, CASE, 'https://nolankido.com/poker/'):
            matches = [e for e in sitemap if e.findtext('{*}loc') == url]
            self.assertEqual(len(matches), 1, url)
            self.assertEqual(matches[0].findtext('{*}lastmod'), '2026-11-19')

    def test_mutations_catch_unsupported_claims_and_broken_sources(self):
        for changed in (
            self.source.replace('draft captions are not verified as part of a released video',
                                'draft captions were verified in the current released video', 1),
            self.source.replace('not verified solver findings', 'verified solver findings', 1),
            self.source.replace('The checker does not inspect video frames or approve a publication',
                                'The checker independently approves the published video', 1),
            self.source.replace('that a product achieved a measured business result',
                                'that a product has proven commercial adoption', 1),
            self.source.replace('href="' + YOUTUBE + '">NolanPoker</a>',
                                'href="https://example.invalid">NolanPoker</a>', 1),
            self.source.replace('href="/downloads/poker-vlog-fact-gate.py"',
                                'href="/downloads/no-check.py"', 1),
        ):
            with self.subTest(differs=changed != self.source):
                self.assertNotEqual(changed, self.source)
                self.assertTrue(bridge_errors(changed))


if __name__ == '__main__':
    unittest.main()
