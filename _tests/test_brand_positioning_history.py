"""The current branding release and the prior release remain separately auditable."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
import build
import brand_positioning_history as history


class BrandPositioningHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.change = history.change()
        cls.outputs = build.build_outputs()

    def test_matching_release_bytes_reconstruct_the_pre_brand_release(self):
        self.assertEqual(len(self.change['paths']), 101)
        for path, item in self.change['paths'].items():
            with self.subTest(path=path):
                raw = (ROOT / path).read_bytes()
                if sha256(raw).hexdigest() != item['new_sha256']:
                    # A later published change must remain visible to the next
                    # history adapter, not fail this archived release's test.
                    self.assertEqual(history.before(path, raw), raw)
                    continue
                previous = history.before(path, raw)
                self.assertEqual(sha256(previous).hexdigest(), item['old_sha256'])
                self.assertEqual(history.before(path, previous), previous)
                if 'old_base64' not in item:
                    self.assertEqual(history.before(path, raw.decode('utf-8')),
                                     previous.decode('utf-8'))

    def test_unreviewed_edits_do_not_get_hidden_by_the_history_adapter(self):
        for path in ['_source/home.html', '_source/pages.json', 'index.html',
                     'technology/index.html', 'assets/social/nolan-kido.png']:
            raw = (ROOT / path).read_bytes()
            for altered in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw, raw[1:]):
                self.assertEqual(history.before(path, altered), altered)
        self.assertEqual(history.before('not-a-release.txt', b'unknown'), b'unknown')

    def test_page_metadata_reverses_only_the_three_approved_records(self):
        pages = build.public_pages()
        restored = history.pages(pages)
        for page, previous in zip(pages, restored):
            if page['id'] in self.change['pages']:
                for key, value in self.change['pages'][page['id']]['old'].items():
                    self.assertEqual(previous[key], value)
            else:
                self.assertEqual(page, previous)
        altered = deepcopy(pages)
        altered[0]['description'] = 'A fabricated result.'
        self.assertEqual(history.pages(altered)[0], altered[0])

    def test_visible_entry_pages_keep_machine_identity_separate_from_readers(self):
        for relative in ['index.html', 'about/index.html', 'technology/index.html']:
            html = self.outputs[Path(relative)]
            self.assertIn('AI Works Human Decides', html)
            self.assertNotIn('Hawaii Dental Clinic and Affiliates', html)
            self.assertNotIn('nolan-kido-headshot.jpg', html)
            self.assertNotIn('/assets/nolan-kido-identity.jsonld', html)
        identity = json.loads((ROOT / 'assets/nolan-kido-identity.jsonld').read_text(encoding='utf-8'))
        person = next(node for node in identity['@graph'] if node['@type'] == 'Person')
        self.assertEqual(person['name'], 'Nolan Kido')
        self.assertIn('Former Chief Operating Officer', person['description'])
        self.assertNotIn('assets/nolan-kido-headshot.jpg', self.change['paths'])
        self.assertNotIn('assets/nolan-kido-headshot-square.jpg', self.change['paths'])


if __name__ == '__main__':
    unittest.main()
