"""Local AI gaming laptop publication, privacy and reproducible script tests.

All tests are local. Only the optional model check itself can contact Ollama,
and that tool is never executed against a real model by this test module.
"""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

from test_site import ROOT, build
import build_local_laptop_case
import local_laptop_case
import manual_local_ai_feed
import practical_discovery
import follow
import site_find
import player_find


class Tags(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.names = []
        self.ids = []
        self.hrefs = []
        self.feed(html)

    def handle_starttag(self, name, attrs):
        attrs = dict(attrs)
        self.names.append(name)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if name == 'a':
            self.hrefs.append(attrs.get('href'))


class LocalLaptopCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / local_laptop_case.SOURCE).read_text(encoding='utf-8')
        cls.html = (ROOT / local_laptop_case.OUTPUT).read_text(encoding='utf-8')
        cls.tags = Tags(cls.html)

    def test_source_is_exactly_compiled_and_canonical(self):
        self.assertEqual(build_local_laptop_case.render(), self.html)
        self.assertIn(self.source, self.html)
        self.assertEqual(self.tags.names.count('h1'), 1)
        self.assertEqual(self.tags.ids.count('laptop-measure'), 1)
        self.assertEqual(len(self.tags.ids), len(set(self.tags.ids)))
        self.assertEqual(local_laptop_case.record(ROOT)['url'], local_laptop_case.URL)
        self.assertNotIn(build.MARKER, self.html)
        self.assertNotIn(chr(0x2014), self.html)
        for doc in (
            'https://ollama.com/download/windows',
            'https://docs.ollama.com/api/generate',
            'https://lmstudio.ai/docs/app/offline',
            'https://lmstudio.ai/docs/developer/openai-compat',
        ):
            self.assertIn(doc, self.tags.hrefs)

    def test_no_unsubstantiated_hardware_or_laptop_performance_claim(self):
        for phrase in ('I have not run a new timed model benchmark on that laptop',
                       'Ubuntu CPU runner hosted by GitHub', 'unmeasured',
                       'does not make the work free', 'human approval'):
            self.assertIn(phrase, self.source)
        self.assertNotIn('<iframe', self.html)
        self.assertNotIn('—', self.html)
        self.assertNotIn('secret_key', self.html)
        self.assertNotIn('YOUR_API_KEY', self.html)

    def test_main_sitemap_search_discovery_and_read_only_live_target(self):
        outputs = build.build_outputs()
        actual = outputs[Path('sitemap.xml')]
        self.assertEqual(actual, (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))
        urls = [n.text for n in ET.fromstring(actual).iter() if n.tag.endswith('}loc')]
        self.assertEqual(urls.count(local_laptop_case.URL), 1)
        self.assertEqual(len(urls), len(set(urls)))
        find_items = player_find.add(ROOT, site_find.entries(ROOT, build.public_pages()))
        self.assertEqual(len([i for i in find_items if i['path'] == local_laptop_case.ROUTE]), 1)
        self.assertEqual(find_items[[i['path'] for i in find_items].index(local_laptop_case.ROUTE)]['home'], 'technology')
        self.assertEqual(outputs[Path('find/index.html')], (ROOT / 'find/index.html').read_text(encoding='utf-8'))
        import check_live
        targets = check_live.targets()
        self.assertEqual(targets[local_laptop_case.ROUTE], (200, self.html.encode('utf-8')))
        self.assertEqual(targets['/' + local_laptop_case.TOOL.as_posix()],
                         (200, (ROOT / local_laptop_case.TOOL).read_bytes()))

    def test_article_is_listed_once_in_technology_and_combined_rss(self):
        pages = build.public_pages()
        outputs = build.build_outputs()
        config = practical_discovery.load(ROOT, pages)
        base = practical_discovery.feed(config, pages, outputs, 'https://nolankido.com')
        tech = manual_local_ai_feed.add(base, ROOT)
        self.assertEqual(tech, outputs[practical_discovery.FEED])
        items = ET.fromstring(tech).findall('./channel/item')
        self.assertEqual([i.findtext('link') for i in items].count(local_laptop_case.URL), 1)
        self.assertEqual(items[0].findtext('pubDate'), 'Mon, 02 Nov 2026 00:00:00 GMT')
        self.assertEqual(outputs[follow.OUTPUT], (ROOT / follow.OUTPUT).read_text(encoding='utf-8'))
        combined = ET.fromstring(outputs[follow.OUTPUT]).findall('./channel/item')
        selected = [i for i in combined if i.findtext('link') == local_laptop_case.URL]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].find('source').get('url'), 'https://nolankido.com/technology/feed.xml')
        with self.assertRaisesRegex(ValueError, 'twice'):
            manual_local_ai_feed.add(tech, ROOT)

    def test_fails_closed_on_broken_canonical_source_or_missing_script(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            paths = (local_laptop_case.SOURCE, local_laptop_case.OUTPUT,
                     local_laptop_case.TOOL, Path('technology/index.html'))
            for rel in paths:
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, dst)
            self.assertEqual(local_laptop_case.record(root)['url'], local_laptop_case.URL)
            target = root / local_laptop_case.OUTPUT
            original = target.read_text(encoding='utf-8')
            for changed in (
                original.replace('<link rel="canonical" href="' + local_laptop_case.URL + '">',
                                 '<link rel="canonical" href="https://example.invalid/">', 1),
                original.replace('<head>', '<head><meta name="robots" content="noindex">', 1),
                original.replace(self.source, '<article><p>unreviewed replacement</p></article>', 1),
            ):
                with self.subTest(change=changed[:80]):
                    target.write_text(changed, encoding='utf-8')
                    with self.assertRaises(ValueError):
                        local_laptop_case.record(root)
            target.write_text(original, encoding='utf-8')
            (root / local_laptop_case.TOOL).unlink()
            with self.assertRaises(ValueError):
                local_laptop_case.record(root)

    def test_downloaded_test_script_is_dry_run_only_unless_explicitly_invoked(self):
        script = ROOT / local_laptop_case.TOOL
        done = subprocess.run([sys.executable, str(script), '--dry-run'],
                              capture_output=True, text=True, check=False, timeout=15)
        self.assertEqual(done.returncode, 0, done.stderr)
        record = json.loads(done.stdout)
        self.assertEqual(record['execution'], 'dry_run')
        self.assertEqual(record['destination'], 'http://127.0.0.1:11434/api/generate')
        self.assertIsNone(record['wall_seconds'])
        self.assertIsNone(record['tokens_per_second'])
        self.assertEqual(record['human_quality_review'], 'not_performed')
        self.assertTrue(record['fixture_sha256'])
        denied = subprocess.run([sys.executable, str(script), '--model', 'any:cloud', '--dry-run'],
                                capture_output=True, text=True, check=False, timeout=15)
        self.assertNotEqual(denied.returncode, 0)


if __name__ == '__main__':
    unittest.main()
