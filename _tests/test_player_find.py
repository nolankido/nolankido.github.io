"""Source-backed tournament player in Find without expanding public manifest.

Run locally with python -m unittest discover -s _tests -p test_player_find.py -v.
No CI, browser automation, network, user-query logging, or private content.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil
import subprocess
import unittest

from test_site import ROOT, Page, build
import site_find
import player_find
import player_sitemap


class PlayerFindTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.manifest_items = site_find.entries(ROOT, cls.pages)
        cls.items = player_find.add(ROOT, cls.manifest_items)
        cls.rendered = build.build_outputs()[Path('find/index.html')]

    def test_profile_is_one_verified_public_search_record(self):
        records = [p for p in self.items if p['path'] == player_sitemap.ROUTE]
        self.assertEqual(len(records), 1)
        entry = records[0]
        self.assertEqual(entry['title'], 'Nolan Kido: Tournament Poker Player')
        self.assertEqual(entry['kind'], 'profile')
        self.assertEqual(entry['interests'], ['poker'])
        self.assertEqual(entry['home'], 'poker')
        self.assertEqual(entry['date'], '')
        self.assertIn('WSOP', entry['description'])
        self.assertIn('tournament poker', entry['description'])
        self.assertEqual(len(self.items), len(self.manifest_items) + 5)
        self.assertNotIn(player_sitemap.ROUTE, {p['path'] for p in self.pages})
        self.assertEqual({p['path'] for p in self.items},
                         {p['path'] for p in self.manifest_items} | {player_sitemap.ROUTE, '/poker/episodes/portland-meadows-ep1/', '/poker/episodes/portland-meadows-standoff/', '/technology/local-ai-gaming-laptop/', '/technology/review-reply-evidence-audit/'})

    def test_existing_find_groups_and_progressive_filter_remain(self):
        html = self.rendered
        parsed = Page(html)
        links = [a.get('href') for a in parsed.tags('a')]
        self.assertEqual(links.count(player_sitemap.ROUTE), 1)
        self.assertEqual(len([d for d in parsed.tags('details')
                              if d.get('class') == 'find-group']), 5)
        self.assertIn('id="browse-poker"><summary>Poker <span class="find-group-count" hidden>(95)</span>', html)
        self.assertIn('<option value="profile">Player profiles</option>', html)
        self.assertIn('data-kind="profile" data-interests="poker"', html)
        self.assertIn('id="find-section-data"', html)
        self.assertIn('Filtering happens on this page.', html)
        self.assertEqual(html, (ROOT / 'find/index.html').read_text(encoding='utf-8'))
        self.assertIn(site_find.render(self.items), html)
        self.assertNotIn('href="' + player_sitemap.ROUTE + '#', html)

    def test_node_matching_finds_real_player_without_remote_search(self):
        code = """
const assert=require('node:assert/strict');
const {score}=require('./assets/site-find.js');
const r=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
const item={...r, subjects:'Poker'};
for (const query of ['Nolan Kido','tournament player','WSOP','poker player']) {
  assert(score(item,query)>=0, query);
}
assert.equal(score(item,'unrelatednewthingz'),-1);
"""
        p = player_find.entry(ROOT)
        result = subprocess.run(['node', '-e', code], cwd=ROOT,
                                input=json.dumps(p), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_profile_metadata_tampering_is_rejected(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            paths = [player_sitemap.RELATIVE, player_sitemap.SOURCE,
                     Path('poker/index.html'), Path('about/index.html')]
            for path in paths:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, dest)
            self.assertEqual(player_find.entry(root)['path'], player_sitemap.ROUTE)
            index = root / player_sitemap.RELATIVE
            original = index.read_text(encoding='utf-8')
            changed = original.replace('name="description" content="',
                                       'name="description" content="INACCURATE ', 1)
            self.assertNotEqual(original, changed)
            index.write_text(changed, encoding='utf-8')
            with self.assertRaises(ValueError):
                player_find.entry(root)
            index.write_text(original, encoding='utf-8')
            (root / player_sitemap.SOURCE).unlink()
            with self.assertRaises(ValueError):
                player_find.entry(root)

    def test_no_profile_in_a_minimal_root_is_not_fabricated(self):
        with TemporaryDirectory() as folder:
            self.assertIsNone(player_find.entry(Path(folder)))
            baseline = [{'path': '/poker/', 'title': 'Poker'}]
            self.assertEqual(player_find.add(Path(folder), baseline), baseline)
        with self.assertRaises(ValueError):
            player_find.add(ROOT, [*self.manifest_items, player_find.entry(ROOT)])


if __name__ == '__main__':
    unittest.main()
