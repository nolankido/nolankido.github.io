"""Later brand metadata and earlier profile history compose without hiding edits."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import answer_review_growth_history as guide_history
import brand_positioning_history as brand_history
import build
import turn10_profile_history as profile_history
from reviewed_release import read as reviewed_bytes


class BrandHistoryCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # These assertions describe the older brand/profile boundary. The
        # newer leaf separately tests full-record mutation rejection.
        release = brand_history.change()['release_commit']
        raw = reviewed_bytes(release, '_source/pages.json',
                             '4ac979a431290dbb4838de3fc370b2ed4b74a416')
        if sha256(raw).hexdigest() != brand_history.change()['paths']['_source/pages.json']['new_sha256']:
            raise AssertionError('Archived brand manifest does not match reviewed release ledger')
        cls.pages = json.loads(raw)

    def test_known_metadata_reaches_the_existing_profile_boundary(self):
        previous = {page['id']: page for page in profile_history.pages(self.pages)}
        for page_id, pair in brand_history.change()['pages'].items():
            expected = deepcopy(pair['old'])
            if page_id == 'about':
                expected['updated'] = '2026-10-12'
            with self.subTest(page=page_id):
                for key, value in expected.items():
                    self.assertEqual(previous[page_id][key], value)
        self.assertEqual(previous['bio']['updated'], '2026-10-11')

    def test_brand_metadata_is_reversed_before_earlier_metadata_histories(self):
        observed = []

        def record_input(records):
            observed.append(deepcopy(records))
            return deepcopy(records)

        with patch.object(guide_history, 'pages', side_effect=record_input):
            profile_history.pages(self.pages)
        self.assertEqual(observed, [brand_history.pages(self.pages)])

    def test_unreviewed_brand_fields_remain_visible(self):
        for page_id, pair in brand_history.change()['pages'].items():
            original = next(page for page in self.pages if page['id'] == page_id)
            for field in pair['new']:
                altered = deepcopy(original)
                altered[field] = 'Unreviewed metadata revision'
                with self.subTest(page=page_id, field=field):
                    self.assertEqual(profile_history.pages([altered]), [altered])

    def test_unrelated_mutations_are_not_discarded(self):
        original = next(page for page in self.pages if page['id'] == 'home')
        altered = deepcopy(original)
        altered['title'] = 'Unreviewed visible heading'
        altered['extra_claim'] = 'Unreviewed assertion'
        previous = profile_history.pages([altered])[0]
        self.assertEqual(previous['title'], altered['title'])
        self.assertEqual(previous['extra_claim'], altered['extra_claim'])
        self.assertEqual(previous['seo_title'],
                         brand_history.change()['pages']['home']['old']['seo_title'])
        self.assertNotEqual(previous, profile_history.pages([original])[0])

    def test_composition_is_idempotent_and_does_not_mutate_inputs(self):
        current = deepcopy(self.pages)
        saved = deepcopy(current)
        previous = profile_history.pages(current)
        self.assertEqual(current, saved)
        self.assertEqual(profile_history.pages(previous), previous)
        previous[0]['title'] = 'Changed only in the returned view'
        self.assertEqual(current, saved)

    def test_old_profile_dates_are_pinned_even_after_new_site_releases(self):
        previous = profile_history.pages(self.pages)
        dates = {page['id']: page['updated'] for page in previous if 'updated' in page}
        self.assertEqual(dates['bio'], '2026-10-11')
        self.assertEqual(dates['about'], '2026-10-12')
        # The current manifest has since been independently edited.
        today = {page['id']: page['updated'] for page in build.public_pages()
                 if 'updated' in page}
        self.assertNotEqual(today['bio'], dates['bio'])

    def test_corrupted_original_profile_dates_fail_closed(self):
        original = profile_history.records()
        altered = deepcopy(original)
        altered['_source/pages.json']['old_sha256'] = '0' * 64
        with patch.object(profile_history, 'records', return_value=altered), \
                self.assertRaisesRegex(ValueError, 'predecessor digest'):
            profile_history.pages(self.pages)


if __name__ == '__main__':
    unittest.main()
