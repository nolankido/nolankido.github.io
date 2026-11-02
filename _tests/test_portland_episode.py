"""Portland Meadows public video companion, source, and safe release gates."""
import json
from pathlib import Path
import re
import shutil
from tempfile import TemporaryDirectory
import unittest
from test_site import ROOT, Page, build

import build_poker_episode
import poker_episode
import poker_content


class PublicPortlandEpisodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / poker_episode.SOURCE).read_text(encoding='utf-8')
        cls.html = (ROOT / poker_episode.OUTPUT).read_text(encoding='utf-8')
        cls.poker_hub = build.build_outputs()[Path('poker/index.html')]
        cls.doc = Page(cls.html)

    def test_companion_is_reproducible_from_approved_source(self):
        self.assertEqual(self.html, build_poker_episode.render())
        self.assertIn(self.source, self.html)
        self.assertNotIn(build.MARKER, self.html)
        self.assertNotIn('—', self.html)
        self.assertNotIn('<iframe', self.html)
        self.assertNotIn('<form', self.html)
        self.assertEqual(len(self.doc.tags('h1')), 1)
        self.assertEqual(len(self.doc.tags('main')), 1)
        self.assertEqual(len(self.doc.tags('title')), 1)
        self.assertEqual(len([x for x in self.doc.tags('nav') if x.get('aria-label') == 'Breadcrumb']), 1)

    def test_verified_video_is_linked_not_embedded(self):
        self.assertEqual(poker_episode.record(ROOT)['video_url'], 'https://www.youtube.com/watch?v=JToB7upHqEM')
        self.assertIn('Portland Meadows Ep1 v7', self.html)
        for seconds in (0, 249, 368, 540, 647, 700):
            self.assertIn('watch?v=JToB7upHqEM&amp;t=' + str(seconds) + 's', self.html)
        self.assertEqual(self.html.count('class="poker-watch"'), 0)
        self.assertNotIn('youtube-nocookie.com/embed', self.html)
        self.assertIn('$2,900', self.html)
        self.assertIn('$5,100', self.html)
        self.assertIn('gross tournament payment, not net profit', self.html)
        self.assertIn('not a verified solver result', self.html)
        self.assertIn('id="hand-64o-record"', self.html)
        self.assertIn('id="hand-77-record"', self.html)

    def test_canonical_schema_author_and_publication_date(self):
        self.assertEqual([x.get('href') for x in self.doc.tags('link')
                          if x.get('rel') == 'canonical'], [poker_episode.URL])
        metas = self.doc.tags('meta')
        self.assertEqual([m.get('content') for m in metas if m.get('property') == 'og:url'], [poker_episode.URL])
        self.assertEqual([m.get('content') for m in metas if m.get('property') == 'og:type'], ['article'])
        records = re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.html, re.S)
        self.assertEqual(len(records), 1)
        record = json.loads(records[0])
        self.assertEqual(record['@type'], 'Article')
        self.assertEqual(record['@id'], poker_episode.URL + '#article')
        self.assertEqual(record['datePublished'], '2026-11-02')
        self.assertEqual(record['author']['@id'], poker_episode.PERSON_ID)
        self.assertEqual(record['mainEntityOfPage']['breadcrumb']['itemListElement'][-1]['item'],
                         poker_episode.URL)
        self.assertFalse(any('noindex' in m.get('content', '').lower()
                             for m in metas if m.get('name') == 'robots'))

    def test_poker_hub_and_player_page_do_not_claim_no_published_video(self):
        self.assertIn('href="' + poker_episode.ROUTE + '"', self.poker_hub)
        self.assertIn('Companion published November 2, 2026.', self.poker_hub)
        self.assertNotIn('No vlog episodes or tournament stories are published on this site yet.', self.poker_hub)
        self.assertEqual(self.poker_hub, (ROOT / 'poker/index.html').read_text(encoding='utf-8'))
        profile = (ROOT / 'poker/nolan-kido/index.html').read_text(encoding='utf-8')
        self.assertIn('href="' + poker_episode.ROUTE + '"', profile)
        self.assertNotIn('There are no published vlog episodes', profile)
        self.assertIn('href="/poker/free-poker-learning-path/"', self.poker_hub)

    def test_missing_or_unreviewed_video_source_is_not_published(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertIsNone(poker_episode.record(root))
            for path in (poker_episode.SOURCE, poker_episode.OUTPUT):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
            self.assertEqual(poker_episode.record(root)['route'], poker_episode.ROUTE)
            output = root / poker_episode.OUTPUT
            original = output.read_text(encoding='utf-8')
            changes = [
                original.replace('<link rel="canonical" href="' + poker_episode.URL + '">',
                                 '<link rel="canonical" href="https://example.invalid/">', 1),
                original.replace('<head>', '<head><meta name="robots" content="noindex">', 1),
                original.replace('JToB7upHqEM', 'nonpublic000', 1),
                original.replace(self.source, '<p>unsupported editing claims</p>', 1)
            ]
            for modified in changes:
                with self.subTest(modified=modified[:70]):
                    self.assertNotEqual(original, modified)
                    output.write_text(modified, encoding='utf-8')
                    with self.assertRaises(ValueError):
                        poker_episode.record(root)
            output.unlink()
            with self.assertRaises(ValueError):
                poker_episode.record(root)


if __name__ == '__main__':
    unittest.main()
