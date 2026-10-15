"""Reader entry paths, exact article preservation and finite native navigation."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
import html5lib
from test_site import ROOT, build
import poker_discovery
import poker_routes_history as history
import poker_course_history


class PokerDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.entries = build.poker_library.load(ROOT, cls.pages)
        cls.config = poker_discovery.load(ROOT, cls.entries)
        cls.baseline = json.loads((ROOT / '_tests/poker-routes-baseline.json').read_text())

    def test_predecessor_is_reconstructed_without_refreshing_old_contracts(self):
        b = self.baseline
        self.assertEqual(b['commit'], 'f05bea77919b097a53ce341f9dd34f888b6ec841')
        self.assertEqual(history.pages(self.pages), b['pages'])
        previous = poker_course_history.outputs(self.outputs)
        self.assertEqual(set(map(str, previous)), set(b['outputs']))
        for path, value in previous.items():
            self.assertEqual(sha256(history.before(path, value).encode()).hexdigest(), b['outputs'][str(path)], path)
        for path, digest in {**b['files'], **b['extras']}.items():
            self.assertEqual(sha256(history.before(path, (ROOT / path).read_bytes())).hexdigest(), digest, path)

    def test_every_article_and_feed_is_byte_identical(self):
        routes = {p['path'] for p in self.pages if p.get('poker_guide') or p.get('poker_entry') or p.get('note') or p.get('living_well_entry') or p.get('evidence_article') or p.get('worked_guide')}
        for route in routes:
            path = build.output_path(route)
            self.assertEqual(sha256(poker_course_history.before(path,self.outputs[path]).encode()).hexdigest(), self.baseline['outputs'][str(path)], route)
        for path, digest in self.baseline['outputs'].items():
            if path.endswith('feed.xml') or path == 'writing.xml':
                self.assertEqual(sha256(poker_course_history.before(path,self.outputs[Path(path)]).encode()).hexdigest(), digest, path)
        for path, digest in self.baseline['files'].items():
            if path.startswith(('assets/', 'downloads/')):
                self.assertEqual(sha256(poker_course_history.before(path,(ROOT / path).read_bytes())).hexdigest(), digest, path)

    def test_old_hub_fragment_destinations_survive(self):
        for route in poker_discovery.HUBS:
            path = build.output_path(route)
            new = self.outputs[path]
            old = history.before(path, new)
            ids = lambda s: {e.get('id') for e in html5lib.parse(s, namespaceHTMLElements=False).iter() if e.get('id')}
            self.assertTrue(ids(old) <= ids(new), route)
            self.assertIn('id="reading-routes"', new)
            self.assertIn('id="in-depth"', new)

    def test_long_guides_have_direct_unhidden_links_and_current_estimates(self):
        by_slug = {e['slug']: e for e in self.entries}
        for route in poker_discovery.HUBS:
            doc = html5lib.parse(self.outputs[build.output_path(route)], namespaceHTMLElements=False)
            section = next(e for e in doc.iter('section') if e.get('id') == 'in-depth')
            articles = list(section.iter('article'))
            self.assertEqual(len(articles), len(self.config['in_depth']))
            for item, article in zip(self.config['in_depth'], articles):
                guide = by_slug[item['slug']]
                self.assertEqual(next(article.iter('a')).get('href'), guide['route'])
                text = ' '.join(article.itertext())
                self.assertIn(guide['title'], text)
                self.assertIn(f'About {guide["minutes"]} min read', text)
            self.assertFalse(list(section.iter('details')))

    def test_unrelated_changes_are_never_hidden_by_history(self):
        for path in ['_source/poker/home.html', '_scripts/build.py', 'poker/index.html', 'find/index.html']:
            value = (ROOT / path).read_bytes() + b'Unreviewed alteration'
            self.assertEqual(history.before(path, value), value)

    def test_invalid_or_unpublished_route_targets_fail_the_build(self):
        original = self.config
        variants = []
        bad = deepcopy(original); bad['routes'][0]['links'][0]['slug'] = 'unpublished'; variants.append(bad)
        bad = deepcopy(original); bad['in_depth'].append(bad['in_depth'][0]); variants.append(bad)
        bad = deepcopy(original); bad['routes'][1]['id'] = bad['routes'][0]['id']; variants.append(bad)
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / '_source/poker').mkdir(parents=True)
            for bad in variants:
                (root / '_source/poker/reading-routes.json').write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    poker_discovery.load(root, self.entries)

    def test_styles_are_scoped_to_the_hubs_and_checked_live(self):
        for path, source in self.outputs.items():
            if path.suffix == '.html':
                self.assertEqual('/assets/poker-discovery.css?v=' in source, path in {build.output_path(p) for p in poker_discovery.HUBS}, path)
        from check_live import targets
        self.assertIn('/assets/poker-discovery.css', targets())


if __name__ == '__main__':
    unittest.main()
