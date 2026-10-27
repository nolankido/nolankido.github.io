"""Three useful homepage choices with exact historical preservation and no tracking."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import html5lib

from test_site import ROOT, Page, build
import creative_print_history
import homepage_growth_history as history
import task_brief_growth_history as task_growth
import answer_review_growth_history as guide_growth
import later_release_history as later_history

PRIMARY = {
    'use': '/technology/task-brief/',
    'inspect': '/technology/checking-ai-website-changes/',
    'understand': '/notes/keep-the-judgment/',
}
FIRST = {
    'technology': '/technology/task-brief/',
    'living-well': '/living-well/weekly-reset/',
    'poker': '/poker/first-live-tournament/',
    'creative': '/creative/#creative-brief',
}


def digest(value):
    return sha256(value if isinstance(value, bytes) else value.encode('utf-8')).hexdigest()


def fingerprint(records):
    return digest(json.dumps(sorted((str(p), digest(v)) for p, v in records.items()), separators=(',', ':')))


class HomepageGrowthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.home = cls.outputs[Path('index.html')]
        cls.doc = html5lib.parse(cls.home, namespaceHTMLElements=False)
        cls.record = history.change()

    def test_three_distinct_choices_are_before_subjects_and_truthfully_described(self):
        choices = [e for e in self.doc.iter('article') if e.get('data-home-choice')]
        self.assertEqual([e.get('data-home-choice') for e in choices], list(PRIMARY))
        for card in choices:
            links = list(card.iter('a'))
            self.assertEqual(len(links), 1)
            self.assertEqual(links[0].get('href'), PRIMARY[card.get('data-home-choice')])
            self.assertIn(build.output_path(links[0].get('href')), self.outputs)
            self.assertNotIn('hidden', card.attrib)
        self.assertLess(self.home.index('id="home-title"'), self.home.index('data-home-choice="use"'))
        self.assertLess(self.home.index('data-home-choice="understand"'), self.home.index('id="destinations-title"'))
        self.assertIn('No account. No AI runs here.', self.home)
        self.assertIn('not a claim of time savings', self.home)
        self.assertNotIn('Selected practical AI work', self.home)

    def test_secondary_choices_are_native_optional_and_keyboard_reachable(self):
        details = [e for e in self.doc.iter('details') if e.get('class') == 'practical-home']
        self.assertEqual(len(details), 1)
        self.assertNotIn('open', details[0].attrib)
        self.assertEqual(next(details[0].iter('summary')).get('id'), 'practical-home-title')
        links = list(details[0].iter('a'))
        self.assertEqual(len(links), 6)
        self.assertEqual(len({a.get('href') for a in links}), len(links))
        for link in links:
            self.assertNotIn('onclick', link.attrib)
            self.assertNotIn('tabindex', link.attrib)
        self.assertIn('fictional poker hand', ''.join(details[0].itertext()))

    def test_four_first_actions_and_original_home_destinations_survive(self):
        cards = [e for e in self.doc.iter('article') if e.get('class', '').startswith('destination destination-')]
        self.assertEqual([e.get('class').removeprefix('destination destination-') for e in cards], list(FIRST))
        for key, card in zip(FIRST, cards):
            first = [a for a in card.iter('a') if a.get('class') == 'destination-first-link']
            self.assertEqual([a.get('href') for a in first], [FIRST[key]])
        current = Page(self.home)
        self.assertLessEqual(set(self.record['base_home_links']), {a.get('href') for a in current.tags('a')})
        self.assertLessEqual(set(self.record['base_home_ids']), {a.get('id') for _, a in current.elements})

    def test_no_new_runtime_or_changes_to_private_boundaries(self):
        for path, expected in self.record['protected_source_hashes'].items():
            self.assertEqual(digest(history.before(path, (ROOT / path).read_bytes())), expected, path)
        for path in ('index.html', 'start-here/index.html'):
            scripts = [a['src'] for a in Page(self.outputs[Path(path)]).tags('script') if 'src' in a]
            self.assertEqual(scripts, ['https://cloud.umami.is/script.js'])
        self.assertEqual(Page(self.home).tags('form'), [])
        self.assertEqual(Page(self.home).tags('img'), [])

    def test_entire_previous_build_and_source_inventory_are_reconstructed(self):
        previous_outputs = history.outputs(self.outputs)
        self.assertEqual(len(previous_outputs), self.record['base_output_count'])
        self.assertEqual(fingerprint(previous_outputs), self.record['base_output_fingerprint'])
        sources = {p.relative_to(ROOT).as_posix(): p.read_bytes()
                   for folder in ('_source', '_scripts', 'assets', 'downloads')
                   for p in (ROOT / folder).rglob('*')
                   if p.is_file() and '__pycache__' not in p.parts}
        previous_sources = history.source_records(sources)
        self.assertEqual(len(previous_sources), self.record['base_source_count'])
        self.assertEqual(fingerprint(previous_sources), self.record['base_source_fingerprint'])
        self.assertEqual(set(self.record['paths']), {
            '_source/home.html', '_source/pages.json', 'assets/first-steps.css',
            'index.html', 'creative/index.html', 'sitemap.xml'})

    def test_unknown_changes_remain_visible_and_reversal_is_exact(self):
        for path, record in self.record['paths'].items():
            raw = task_growth.before(path, creative_print_history.before(path, (ROOT / path).read_bytes()))
            self.assertEqual(digest(raw), record['new_sha256'], path)
            previous = history.before(path, raw)
            self.assertEqual(digest(previous), record['old_sha256'], path)
            self.assertEqual(history.before(path, previous), previous)
            for altered in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw, raw[1:]):
                self.assertEqual(history.before(path, altered), altered, path)
        self.assertEqual(history.before('unknown.bin', b'\xff\x00'), b'\xff\x00')

    def test_only_actual_homepage_revision_is_reversed_not_other_metadata(self):
        # This assertion belongs to the archived homepage release, before
        # the later independently tested positioning and identity changes.
        records = later_history.pages(build.public_pages())
        home = next(p for p in records if p['id'] == 'home')
        self.assertEqual(home, self.record['pages']['home']['new'])
        self.assertEqual(home['updated'], '2026-10-17')
        self.assertEqual(history.pages([home]), [self.record['pages']['home']['old']])
        unknown = deepcopy(home); unknown['description'] += ' Unreviewed claim'
        self.assertEqual(history.pages([unknown]), [unknown])
        import turn10_profile_history
        for page in records:
            if page['id'] not in {'home', 'task-brief'}:
                # Later About/Bio revision dates are independently approved;
                # restore those dates before checking this earlier release.
                self.assertEqual(history.pages([page]), turn10_profile_history.pages(guide_growth.pages([page])))
        task = next(p for p in records if p['id'] == 'task-brief')
        self.assertEqual(history.pages([task]), [task_growth.change()['page']['old']])

    def test_corrupt_offsets_and_digests_cannot_reconstruct_history(self):
        path = '_source/home.html'
        raw = (ROOT / path).read_bytes()
        for mutation in ('text', 'offset', 'hash'):
            corrupt = deepcopy(self.record)
            item = corrupt['paths'][path]
            if mutation == 'text': item['edits'][0]['new'] += 'corrupt'
            if mutation == 'offset': item['edits'][0]['start'] = -1
            if mutation == 'hash': item['old_sha256'] = '0' * 64
            with self.subTest(mutation=mutation), patch.object(history, 'change', return_value=corrupt), self.assertRaises(ValueError):
                history.before(path, raw)


if __name__ == '__main__':
    unittest.main()
