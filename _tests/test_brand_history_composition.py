"""Later brand metadata and earlier profile history compose without hiding edits."""
from copy import deepcopy
from pathlib import Path
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


class BrandHistoryCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()

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


if __name__ == '__main__':
    unittest.main()
