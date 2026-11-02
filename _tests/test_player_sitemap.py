"""Manual player-profile sitemap registration and public-byte coverage.

Standalone page remains outside the main article manifest; the builder's
canonical sitemap must still advertise its independently reviewed public URL.
No GitHub Actions, network requests, third-party parsers, or credentials.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
import unittest

from test_site import ROOT, build
import player_sitemap


class ManualPlayerSitemapTests(unittest.TestCase):
    def test_registered_profile_is_indexable_and_reachable(self):
        self.assertEqual(player_sitemap.record(ROOT), (player_sitemap.URL, player_sitemap.MODIFIED))
        self.assertTrue((ROOT / player_sitemap.RELATIVE).is_file())
        self.assertNotIn(player_sitemap.ROUTE, {p['path'] for p in build.public_pages()})
        self.assertIn('href="' + player_sitemap.ROUTE + '"',
                      (ROOT / 'poker/index.html').read_text(encoding='utf-8'))
        self.assertIn('href="' + player_sitemap.ROUTE + '"',
                      (ROOT / 'about/index.html').read_text(encoding='utf-8'))

    def test_main_builder_and_committed_sitemap_reproduce_exactly(self):
        generated = build.build_outputs()[Path('sitemap.xml')]
        committed = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertEqual(generated, committed)
        urls = [node.text for node in ET.fromstring(generated).iter()
                if node.tag.endswith('}loc')]
        self.assertEqual(urls.count(player_sitemap.URL), 1)
        self.assertEqual(len(urls), len(set(urls)))
        self.assertEqual(len(urls), len([p for p in build.public_pages() if not p.get('noindex')]) + 4)
        route = next(node for node in ET.fromstring(generated) if any(
            child.tag.endswith('}loc') and child.text == player_sitemap.URL for child in node))
        modified = [child.text for child in route if child.tag.endswith('}lastmod')]
        self.assertEqual(modified, [player_sitemap.MODIFIED])

    def test_manual_profile_is_in_read_only_live_byte_targets(self):
        import check_live
        targets = check_live.targets()
        self.assertEqual(targets[player_sitemap.ROUTE],
                         (200, (ROOT / player_sitemap.RELATIVE).read_bytes()))

    def test_empty_temporary_site_is_not_mistaken_for_a_publication(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertIsNone(player_sitemap.record(root))
            xml = ET.Element('urlset')
            player_sitemap.add_to_sitemap(xml, root)
            self.assertEqual(len(xml), 0)

    def test_missing_source_or_corrupt_player_profile_fails_closed(self):
        original = (ROOT / player_sitemap.RELATIVE).read_text(encoding='utf-8')
        source = (ROOT / player_sitemap.SOURCE).read_text(encoding='utf-8')
        poker = (ROOT / 'poker/index.html').read_text(encoding='utf-8')
        about = (ROOT / 'about/index.html').read_text(encoding='utf-8')
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / player_sitemap.RELATIVE).parent.mkdir(parents=True)
            (root / player_sitemap.SOURCE).parent.mkdir(parents=True)
            for path, text in [
                (player_sitemap.RELATIVE, original), (player_sitemap.SOURCE, source),
                (Path('poker/index.html'), poker), (Path('about/index.html'), about),
            ]:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(text, encoding='utf-8')
            self.assertEqual(player_sitemap.record(root), (player_sitemap.URL, player_sitemap.MODIFIED))
            profile = root / player_sitemap.RELATIVE
            for description, altered in [
                ('canonical', original.replace(
                    '<link rel="canonical" href="' + player_sitemap.URL + '">',
                    '<link rel="canonical" href="https://example.invalid/">', 1)),
                ('noindex', original.replace('<head>', '<head><meta name="robots" content="noindex">', 1)),
                ('date', original.replace('"dateModified": "2026-11-01"',
                                          '"dateModified": "2026-01-01"', 1)),
                ('missing-source-body', original.replace(source, '<div>unverified replacement</div>', 1)),
            ]:
                with self.subTest(description=description):
                    self.assertNotEqual(original, altered)
                    profile.write_text(altered, encoding='utf-8')
                    with self.assertRaises(ValueError):
                        player_sitemap.record(root)
            profile.write_text(original, encoding='utf-8')
            (root / player_sitemap.SOURCE).unlink()
            with self.assertRaises(ValueError):
                player_sitemap.record(root)


if __name__ == '__main__':
    unittest.main()
