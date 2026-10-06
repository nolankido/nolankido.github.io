"""Discovery, privacy, editorial metadata and independent Decision Lab arithmetic."""
from copy import deepcopy
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import shutil
import unittest
from test_site import ROOT, build
import poker_library as library
import check_live

class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.items=[]; self.feed(text)
    def handle_starttag(self, tag, attrs): self.items.append((tag,dict(attrs)))

class PokerLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=build.public_pages(); cls.entries=library.load(ROOT,cls.pages); cls.outputs=build.build_outputs()

    def test_every_guide_and_hand_review_is_indexed_once(self):
        expected={p['path'] for p in self.pages if p.get('poker_guide')}|{'/poker/reviewing-a-hand/'}
        routes=[e['route'] for e in self.entries]
        self.assertEqual(set(routes),expected); self.assertEqual(len(routes),len(expected))
        page=self.outputs[Path('poker/library/index.html')]
        cards=[a for t,a in Tags(page).items if 'data-library-card' in a]
        self.assertEqual(len(cards),len(expected))
        self.assertTrue(all('hidden' not in c for c in cards))
        self.assertIn('id="library-controls" hidden',page)
        for route in expected: self.assertIn(route,page)
        for path in ['poker/index.html','poker/study/index.html','poker/start-here/index.html']:
            self.assertIn('/poker/library/',self.outputs[Path(path)])

    def test_invalid_catalogs_cannot_silently_drop_guides(self):
        original=json.loads((ROOT/'_source/poker/library.json').read_text())
        variants=[]
        missing=deepcopy(original);missing['entries'].pop();variants.append(missing)
        duplicate=deepcopy(original);duplicate['entries'].append(duplicate['entries'][0]);variants.append(duplicate)
        traversal=deepcopy(original);traversal['entries'][0]['slug']='../secret';variants.append(traversal)
        wrong=deepcopy(original);wrong['entries'][0]['topic']='unknown';variants.append(wrong)
        malformed=deepcopy(original);malformed['entries'][0]['keywords']=[];variants.append(malformed)
        with TemporaryDirectory() as d:
            root=Path(d);shutil.copytree(ROOT/'_source',root/'_source')
            for data in variants:
                (root/'_source/poker/library.json').write_text(json.dumps(data))
                with self.assertRaises(ValueError): library.load(root,self.pages)

    def test_reading_estimate_is_explicit_and_excludes_script_text(self):
        self.assertEqual(library.minutes('<p>'+('word '*225)+'</p>'),1)
        self.assertEqual(library.minutes('<p>'+('word '*226)+'</p>'),2)
        self.assertEqual(library.minutes('<script>'+('word '*1000)+'</script><p>Read this</p>'),1)
        self.assertIn('225 words per minute',self.outputs[Path('poker/library/index.html')])
        for entry in self.entries:
            content=self.outputs[build.output_path(entry['route'])]
            self.assertIn(f'About {entry["minutes"]} min read',content)
            self.assertIn('id="reader-next-heading"',content)

    def test_catalog_text_is_escaped(self):
        item={**self.entries[0],'title':'<img src=x onerror=alert(1)>','description':'A & B','keywords':'" unsafe'}
        rendered=library.card(item)
        self.assertNotIn('<img',rendered);self.assertIn('&lt;img',rendered);self.assertIn('A &amp; B',rendered)
        self.assertIn('&quot;',rendered)

    def test_only_the_library_loads_the_local_filter_script(self):
        for path,content in self.outputs.items():
            if path.suffix!='.html':continue
            scripts=[a.get('src') for t,a in Tags(content).items if t=='script' and a.get('src')]
            matches=[s for s in scripts if s.startswith('/assets/poker-library.js?v=')]
            self.assertEqual(len(matches),1 if path==Path('poker/library/index.html') else 0)
            if str(path).startswith('poker/'):
                self.assertIn('/assets/poker-reader.css?v=',content)
            else:
                self.assertNotIn('/assets/poker-reader.css',content)
        script=(ROOT/'assets/poker-library.js').read_text()
        for forbidden in ['fetch(', 'XMLHttpRequest', 'sendBeacon', 'localStorage', 'sessionStorage', 'umami.', 'innerHTML', 'pushState', 'replaceState']:
            self.assertNotIn(forbidden,script)
        self.assertNotIn('<form',self.outputs[Path('poker/library/index.html')])

    def test_new_assets_and_pages_are_in_live_verification(self):
        for route in ['/poker/library/','/poker/decision-lab/','/assets/poker-reader.css','/assets/poker-library.js']:
            self.assertIn(route,check_live.targets())
        for route in ['/poker/library/','/poker/decision-lab/']:
            self.assertIn(route,self.outputs[Path('sitemap.xml')])
        self.assertIn('/poker/decision-lab/',self.outputs[Path('poker/feed.xml')])

    def test_lab_price_weights_and_outcomes_are_independently_correct(self):
        hero='As Qc'.split();board='Ah 7d 2c 9s 3h'.split();value='Ad Kc'.split();bluff='Ks Qs'.split()
        from test_viewer_guides import best
        for villain in [value,bluff]:self.assertEqual(len(set(hero+board+villain)),9)
        self.assertLess(best(hero+board),best(value+board))
        self.assertGreater(best(hero+board),best(bluff+board))
        current=20+10;final=current+10
        self.assertEqual(Fraction(10,final),Fraction(1,4))
        self.assertEqual(Fraction(3,12)*final-10,0)
        weighted=Fraction(3,2)/(9+Fraction(3,2))
        self.assertEqual(weighted,Fraction(1,7))
        self.assertEqual(weighted*final-10,Fraction(-30,7))
        self.assertEqual(final-10,30)
        content=self.outputs[Path('poker/decision-lab/index.html')]
        for phrase in ['25%', '14.3%', '−4.29 BB', '30 BB', 'fictional', 'Prepared with AI assistance.']:
            self.assertIn(phrase,content)
        panels=[a for t,a in Tags(content).items if t=='details' and 'lab-answer' in a.get('class','')]
        self.assertEqual(len(panels),5);self.assertTrue(all('open' not in a for a in panels))
        cards=[a for t,a in Tags(content).items if 'reader-playing-card' in a.get('class','')]
        self.assertEqual(len(cards),7);self.assertTrue(all(' of ' in a.get('aria-label','') for a in cards))

if __name__=='__main__':unittest.main(verbosity=2)
