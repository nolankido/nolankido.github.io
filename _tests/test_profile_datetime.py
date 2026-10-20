"""ProfilePage DateTime repair: exact scope without invented edit timestamps."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import re
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_search
import search_visibility
import profile_datetime_history as history


def digest(value):
    return sha256(value if isinstance(value, bytes) else value.encode('utf-8')).hexdigest()


def fingerprint(items):
    return digest(json.dumps(sorted(items), separators=(',', ':')))


class ProfileDateTimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.site = json.loads((ROOT / '_source/site.json').read_text())
        cls.page = next(p for p in build.public_pages() if p['id'] == 'about')
        cls.html = cls.outputs[Path('about/index.html')]
        cls.old = history.before('about/index.html', cls.html)

    def decorate(self, schema):
        return search_visibility.decorate(self.page, [self.page], self.site,
                                           schema, '', {})[0]

    def test_recorded_predecessor_reproduces_date_only_profile_value(self):
        old = check_search.Document(self.old).schemas[0]
        self.assertEqual(old['@type'], 'ProfilePage')
        self.assertEqual(old['dateModified'], '2026-10-17')

    def test_output_changes_only_the_optional_profile_modified_field(self):
        old = check_search.Document(self.old).schemas[0]
        new = check_search.Document(self.html).schemas[0]
        old.pop('dateModified')
        self.assertEqual(new, old)
        self.assertEqual(new['mainEntity']['@type'], 'Person')
        self.assertEqual(new['mainEntity']['name'], self.site['name'])
        self.assertNotIn('dateCreated', new)
        self.assertEqual(new['url'], 'https://nolankido.com/about/')

    def test_visible_page_and_all_other_head_content_remain_identical(self):
        pattern = r'<script type="application/ld\+json">.*?</script>'
        self.assertEqual(re.sub(pattern, '', self.html, flags=re.S),
                         re.sub(pattern, '', self.old, flags=re.S))

    def test_decorator_omits_day_only_without_mutating_inputs(self):
        for value in ['2026-10-17', '2024-02-29', '2000-01-01']:
            original = {'@type': 'ProfilePage', 'dateModified': value,
                        'mainEntity': {'@type': 'Person', 'name': 'Example'}}
            saved = deepcopy(original)
            result = self.decorate(original)
            self.assertNotIn('dateModified', result)
            self.assertEqual(original, saved)

    def test_independently_supplied_datetimes_are_not_rewritten(self):
        for value in ['2026-10-17T10:30:00Z', '2026-10-17T03:30:00-07:00']:
            original = {'@type': 'ProfilePage', 'dateModified': value}
            self.assertEqual(self.decorate(original)['dateModified'], value)

    def test_dates_on_other_schema_types_are_preserved(self):
        for kind in ['Article', 'WebPage', 'CollectionPage']:
            result = self.decorate({'@type': kind, 'dateModified': '2026-10-17'})
            self.assertEqual(result['dateModified'], '2026-10-17')

    def test_absent_dates_do_not_gain_build_time_or_a_creation_claim(self):
        result = self.decorate({'@type': 'ProfilePage'})
        self.assertNotIn('dateModified', result)
        self.assertNotIn('dateCreated', result)
        self.assertNotIn('datePublished', result)

    def test_original_catalog_and_sitemap_revision_stay_intact(self):
        self.assertEqual(self.page['updated'], '2026-10-17')
        self.assertIn('<loc>https://nolankido.com/about/</loc>\n    <lastmod>2026-10-17</lastmod>',
                      self.outputs[Path('sitemap.xml')])
        self.assertEqual(self.outputs[Path('sitemap.xml')], (ROOT / 'sitemap.xml').read_text())

    def test_entire_production_inventory_restores_exact_published_parent(self):
        record = history.change()
        self.assertEqual(set(record['paths']), {'_scripts/search_visibility.py', 'about/index.html'})
        tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        items = [(p, digest(history.before(p, (ROOT / p).read_bytes())))
                 for p in tracked if p and not p.startswith(('_tests/', '_reports/'))]
        self.assertEqual(len(items), record['production_count'])
        self.assertEqual(fingerprint(items), record['production_fingerprint'])

    def test_current_approved_bytes_and_mutation_rejection(self):
        for path, item in history.change()['paths'].items():
            raw = (ROOT / path).read_bytes()
            self.assertEqual(digest(raw), item['new_sha256'])
            old = history.before(path, raw)
            self.assertEqual(digest(old), item['old_sha256'])
            self.assertEqual(history.before(Path(path), raw.decode()).encode(), old)
            self.assertEqual(history.before(path, old), old)
            for changed in (raw + b'!', b'!' + raw, raw[1:]):
                self.assertEqual(history.before(path, changed), changed)
        self.assertEqual(history.before('other', b'content'), b'content')

    def test_corrupted_predecessor_cannot_mask_a_change(self):
        record = deepcopy(history.change())
        record['paths']['about/index.html']['old_sha256'] = '0' * 64
        with patch.object(history, 'change', return_value=record):
            with self.assertRaises(ValueError):
                history.before('about/index.html', self.html)

    def test_invalid_catalog_date_is_still_rejected_upstream(self):
        for value in ['2026-02-30', '20261017', 'not-a-date']:
            with self.assertRaises(ValueError):
                build.date_value(value)


if __name__ == '__main__':
    unittest.main()
