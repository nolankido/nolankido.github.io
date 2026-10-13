"""Actual-work previews, complete Technology publishing, and historical preservation."""
import choice_history
from copy import deepcopy
from email.utils import parsedate_to_datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from xml.etree import ElementTree as ET
import hashlib
import json
import re
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import follow
import practical_discovery as discovery
import time_export_history


def records(xml):
    return {i.findtext('link'): [(c.tag, sorted(c.attrib.items()), c.text) for c in i]
            for i in ET.fromstring(xml).findall('./channel/item')}


class PracticalDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.config = discovery.load(ROOT, cls.pages)
        cls.outputs = build.build_outputs()
        cls.baseline = json.loads((ROOT / '_tests/practical-discovery-baseline.json').read_text())

    def test_original_personal_intro_articles_and_source_feeds_are_preserved(self):
        for path, digest in self.baseline['protected_files'].items():
            raw = choice_history.read(path)
            if path == '_source/home.html':
                raw = raw.replace(b'    ${practical_home}\n', b'')
            self.assertEqual(hashlib.sha256(raw).hexdigest(), digest, path)
        for path in follow.LEGACY_SOURCES:
            self.assertEqual(self.outputs[path].encode(), (ROOT / path).read_bytes())

    def test_combined_feed_preserves_every_original_record_and_source(self):
        now = records(self.outputs[follow.OUTPUT])
        historical = {url: now[url] for url in self.baseline['combined_urls']}
        self.assertEqual(len(historical), self.baseline['combined_record_count'])
        self.assertEqual(hashlib.sha256(json.dumps(historical, sort_keys=True).encode()).hexdigest(),
                         self.baseline['combined_record_signature'])
        added = set(now) - set(historical)
        self.assertEqual(added, {'https://nolankido.com/technology/checking-ai-website-changes/', 'https://nolankido.com/technology/check-ai-summary/', 'https://nolankido.com/technology/should-i-use-ai/', 'https://nolankido.com/technology/check-ai-answers/'})
        for slug in ['task-brief', 'ai-time-savings']:
            self.assertNotIn('https://nolankido.com/technology/' + slug + '/', now)

    def test_practical_feed_is_exact_canonical_selection_without_duplicates(self):
        tree = ET.fromstring(self.outputs[discovery.FEED])
        items = tree.findall('./channel/item')
        expected = {'https://nolankido.com/notes/' + s + '/' for s in self.config['note_ids']}
        expected.update({'https://nolankido.com/technology/checking-ai-website-changes/', 'https://nolankido.com/technology/check-ai-summary/', 'https://nolankido.com/technology/should-i-use-ai/', 'https://nolankido.com/technology/check-ai-answers/'})
        self.assertEqual({i.findtext('link') for i in items}, expected)
        self.assertEqual(len(items), len(expected))
        original = records(self.outputs[Path('feed.xml')])
        for url, signature in records(self.outputs[discovery.FEED]).items():
            if url in original:
                self.assertEqual(signature, original[url])
        keys = [(-parsedate_to_datetime(i.findtext('pubDate')).timestamp(), i.findtext('link')) for i in items]
        self.assertEqual(keys, sorted(keys))
        ch = tree.find('channel')
        self.assertEqual(ch.find('{http://www.w3.org/2005/Atom}link').get('href'), 'https://nolankido.com/technology/feed.xml')

    def test_later_published_cases_automatically_reach_writing_and_both_feeds(self):
        pages = deepcopy(self.pages)
        case = deepcopy(discovery.articles(pages)[0])
        case.update(id='second-case', path='/technology/second-case/', title='A second recorded case',
                    source='technology/second-case.html')
        pages.append(case)
        outputs = dict(self.outputs)
        outputs[discovery.FEED] = discovery.feed(self.config, pages, outputs, 'https://nolankido.com')
        combined = follow.combined(outputs, pages, 'https://nolankido.com')
        self.assertEqual(len(records(combined)), len(records(self.outputs[follow.OUTPUT])) + 1)
        self.assertIn('href="/technology/second-case/"', discovery.article_cards(pages))
        for mutation in [{'noindex': True}, {'draft': True}, {'date': None}, {'path': '//other.example/x/'}, {'date': '2026-02-30'}]:
            invalid = deepcopy(pages)
            invalid[-1].update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                discovery.articles(invalid)

    def test_configuration_rejects_wrong_identity_kind_or_preview(self):
        mutations = [lambda c: c.update(works=[]), lambda c: c.update(note_ids=[None]),
                     lambda c: c['works'][0].update(id='technology'),
                     lambda c: c['works'][0].update(kind='case'),
                     lambda c: c['works'][0]['image'].update(src='https://other.example/image.png'),
                     lambda c: c['works'][0]['image'].update(width=1),
                     lambda c: c['works'][1].update(id='task-brief'),
                     lambda c: c.update(note_ids=['task-brief'])]
        for mutate in mutations:
            config = deepcopy(self.config); mutate(config)
            with self.subTest(config=config), patch.object(discovery.json, 'loads', return_value=config), self.assertRaises(ValueError):
                discovery.load(ROOT, self.pages)

    def test_renderers_escape_editorial_text_and_do_not_mutate(self):
        config, pages = deepcopy(self.config), deepcopy(self.pages)
        config['works'][0]['summary'] = '<script>bad</script> & text'
        config['works'][0]['image']['alt'] = '"><img src=x>'
        case = next(p for p in pages if p.get('evidence_article'))
        case['title'] = '<iframe>not markup</iframe>'
        before = deepcopy((config, pages, self.outputs))
        html = discovery.home_links(config, pages) + discovery.work_cards(config, pages) + discovery.article_cards(pages)
        self.assertNotIn('<script>', html)
        self.assertNotIn('<iframe>', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertEqual((config, pages, self.outputs), before)
        for origin in ['http://nolankido.com', 'https://nolankido.com/', 'https://nolankido.com?q=1']:
            with self.assertRaises(ValueError):
                discovery.feed(config, pages, self.outputs, origin)

    def test_real_capture_provenance_matches_pixels_and_reviewed_historical_dependencies(self):
        records_ = json.loads((ROOT / '_reports/work-preview-provenance.json').read_text())
        self.assertEqual({r['id'] for r in records_}, {'task-brief', 'ai-time-savings'})
        by_id = {w['id']: w for w in self.config['works']}
        for r in records_:
            raw = (ROOT / r['src'].lstrip('/')).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), r['sha256'])
            self.assertEqual(struct.unpack('>II', raw[16:24]), (r['width'], r['height']))
            self.assertLess(len(raw), 160_000)
            self.assertEqual(r['input_basis'], 'fictional teaching example')
            self.assertIn('excerpt', r['capture'])
            self.assertIn('fictional', by_id[r['id']]['image']['caption'])
            for path, digest in r['dependencies'].items():
                # Keep the actual capture record. The exact export-only handler
                # change is reversed here; normal result pixels are independently
                # compared with that historical script in the hosted browser suite.
                captured=time_export_history.before(path,(ROOT / path).read_bytes())
                self.assertEqual(hashlib.sha256(captured).hexdigest(), digest, path)

    def test_discovery_is_native_complete_scoped_and_free_of_new_scripts(self):
        home = self.outputs[Path('index.html')]
        tech = self.outputs[Path('technology/index.html')]
        writing = self.outputs[Path('notes/index.html')]
        for w in self.config['works']:
            p = next(p for p in self.pages if p['id'] == w['id'])
            self.assertIn('href="' + p['path'] + '"', home)
            self.assertIn('href="' + p['path'] + '"', tech)
        self.assertEqual(home.count('class="practical-home"'), 1)
        self.assertLess(home.index('A personal introduction'), home.index('class="practical-home"'))
        self.assertLess(home.index('class="identity-reading'), home.index('class="practical-home"'))
        self.assertEqual(writing.count('class="section folio-row writing-route"'), 4)
        self.assertEqual(writing.count('technology-publication'), len(discovery.articles(self.pages)))
        for p in self.pages:
            html = self.outputs[build.output_path(p['path'])]
            self.assertEqual('/assets/practical-discovery.css?' in html, p['id'] in discovery.SCOPED_IDS)
            self.assertEqual('href="/technology/feed.xml"' in html.split('</head>')[0], (p.get('section') == 'technology' or p['id'] == 'technology'))
        for im in re.findall(r'<img\b[^>]+>', tech):
            self.assertIn('loading="lazy"', im)
            self.assertIn('width="1044" height="600"', im)
            self.assertIn('alt="', im)
        for key in ['practical_home', 'practical_work']:
            self.assertNotIn('${' + key + '}', home + tech)

    def test_feed_and_preview_assets_are_exact_live_targets(self):
        targets = check_live.targets()
        for path in ['technology/feed.xml', 'assets/practical-discovery.css',
                     'assets/work/task-brief-preview.png', 'assets/work/ai-time-savings-preview.png']:
            self.assertEqual(targets['/' + path], (200, (ROOT / path).read_bytes()))
        self.assertIn('id="practical-ai-feed"', self.outputs[Path('follow/index.html')])
        article = self.outputs[Path('technology/checking-ai-website-changes/index.html')]
        self.assertIn('href="/follow/#practical-ai-feed"', article)
        self.assertIn('href="/notes/#technology"', article)


if __name__ == '__main__':
    unittest.main()
