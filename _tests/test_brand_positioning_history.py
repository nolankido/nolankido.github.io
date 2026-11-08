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
import scoped_share_history
import public_source_review_history
from reviewed_release import read as reviewed_bytes


BRAND_RELEASE_BLOBS = {
    '_source/pages.json': '4ac979a431290dbb4838de3fc370b2ed4b74a416',
    '_scripts/practical_path.py': 'f4242e1c7ec033b22fd546bd4646b4d635f0d017',
    'index.html': 'a07cf77a51ef8387eccb7e3f16b138c4968cf90d',
    'about/index.html': '1f7474c8101a5b0a1b1f4ae387b195caab3b205d',
    'technology/index.html': '833b66940a14dd89656d9cd37ecb6311dd730d48',
}


def brand_release_bytes(path):
    return reviewed_bytes(history.change()['release_commit'], path,
                          BRAND_RELEASE_BLOBS[path])


class BrandPositioningHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.change = history.change()
        cls.outputs = build.build_outputs()

    def test_matching_release_bytes_reconstruct_the_pre_brand_release(self):
        self.assertEqual(len(self.change['paths']), 101)
        for path, item in self.change['paths'].items():
            with self.subTest(path=path):
                # Compare this archived layer with its actual successor bytes,
                # after the newer independently checked source review is undone.
                raw = public_source_review_history.before(path, (ROOT / path).read_bytes())
                scoped = scoped_share_history.change()['paths'].get(path)
                if scoped and sha256(raw).hexdigest() == scoped['current_sha256']:
                    previous = history.before(path, raw)
                    self.assertEqual(sha256(previous).hexdigest(), item['old_sha256'])
                    self.assertEqual(history.before(path, previous), previous)
                    continue
                if sha256(raw).hexdigest() != item['new_sha256']:
                    # Subsequent independently reviewed history may rewind
                    # this file directly to the brand predecessor. A genuinely
                    # unknown edit must still remain visible.
                    converted = history.before(path, raw)
                    if converted != raw:
                        self.assertEqual(sha256(converted).hexdigest(),
                                         item['old_sha256'])
                        if path in BRAND_RELEASE_BLOBS:
                            self.assertEqual(converted, history.before(
                                path, brand_release_bytes(path)))
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

    def test_changed_archived_brand_bytes_remain_visible(self):
        for path in ('_source/pages.json', '_scripts/practical_path.py',
                     'technology/index.html'):
            original = brand_release_bytes(path)
            for altered in (original + b'UNREVIEWED', b'UNREVIEWED' + original,
                            original[1:]):
                with self.subTest(path=path, digest=sha256(altered).hexdigest()):
                    self.assertEqual(history.before(path, altered), altered)

    def test_page_metadata_reverses_only_the_three_approved_records(self):
        # The brand release contains 108 records. Today's larger manifest is
        # not the historical metadata boundary this archived test describes.
        raw = brand_release_bytes('_source/pages.json')
        self.assertEqual(sha256(raw).hexdigest(),
                         self.change['paths']['_source/pages.json']['new_sha256'])
        current = json.loads(raw)
        pages = public_source_review_history.pages(current)
        restored = history.pages(pages)
        for page, previous in zip(pages, restored):
            if page['id'] in self.change['pages']:
                for key, value in self.change['pages'][page['id']]['old'].items():
                    self.assertEqual(previous[key], value)
            else:
                self.assertEqual(page, previous)
        altered = deepcopy(current)
        altered[0]['description'] = 'A fabricated result.'
        self.assertEqual(history.pages(altered)[0], altered[0])

    def test_archived_entry_pages_kept_machine_identity_separate_from_readers(self):
        for relative in ['index.html', 'about/index.html', 'technology/index.html']:
            raw = brand_release_bytes(relative)
            self.assertEqual(sha256(raw).hexdigest(),
                             self.change['paths'][relative]['new_sha256'])
            html = raw.decode('utf-8')
            self.assertIn('AI Works Human Decides', html)
            self.assertNotIn('Hawaii Dental Clinic and Affiliates', html)
            self.assertNotIn('nolan-kido-headshot.jpg', html)
            self.assertNotIn('/assets/nolan-kido-identity.jsonld', html)
            current_html = self.outputs[Path(relative)]
            self.assertIn('AI Works Human Decides', current_html)
            self.assertNotIn('nolan-kido-headshot.jpg', current_html)
        identity = json.loads((ROOT / 'assets/nolan-kido-identity.jsonld').read_text(encoding='utf-8'))
        person = next(node for node in identity['@graph'] if node['@type'] == 'Person')
        self.assertEqual(person['name'], 'Nolan Kido')
        self.assertIn('Former Chief Operating Officer', person['description'])
        self.assertNotIn('assets/nolan-kido-headshot.jpg', self.change['paths'])
        self.assertNotIn('assets/nolan-kido-headshot-square.jpg', self.change['paths'])


if __name__ == '__main__':
    unittest.main()
