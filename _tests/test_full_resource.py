"""Full-resource release: text extraction, source preservation and independent mathematics."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import json
import shutil
import subprocess
import unittest
from test_site import ROOT, Page, build
from test_resource_collections import lows, high
import poker_finder, poker_library, poker_resources, poker_quality, check_live

NEW = ('omaha-hi-lo-workshop','stud-and-lowball-workshop','multiway-pot-workshop','poker-media-study','poker-access-and-protection')
class FullResourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=build.build_outputs(); cls.pages=build.public_pages(); cls.resources=poker_resources.load(ROOT)
        cls.items=poker_finder.entries(ROOT,cls.pages,poker_library.load(ROOT,cls.pages),cls.resources)

    def test_deeper_guides_and_utilities_keep_the_shared_topic_architecture(self):
        import poker_topics
        topics=poker_topics.load(ROOT,self.pages,poker_library.load(ROOT,self.pages),self.resources)
        primary={slug:t['id'] for t in topics for slug in t['primary_guides']}
        expected={'omaha-hi-lo-workshop':'variants','stud-and-lowball-workshop':'variants',
                  'multiway-pot-workshop':'cash-games','poker-media-study':'poker-world',
                  'poker-access-and-protection':'safer-play'}
        for slug,topic in expected.items():self.assertEqual(primary[slug],topic)
        annotated={e['url']:e for e in poker_topics.annotate(self.items,topics)}
        item=annotated['/poker/multiway-pot-workshop/']
        self.assertTrue({'cash-games','strategy'} <= set(item['topics']))
        self.assertTrue(item['sections'])
        self.assertIn('study',annotated['/poker/study-calculators/']['topics'])
        self.assertIn('safer-play',annotated['/poker/resource-quality/']['topics'])

    def test_article_text_uses_visible_prose_and_existing_anchors(self):
        text='<nav>secret-navigation</nav><p>Intro text</p><h2 id="actual">Actual heading</h2><p>some <strong>bold</strong> words.</p><details><summary>Question</summary><p>hidden-answer</p></details><script>bad script</script><div hidden>private-hidden</div><p>Final public text.</p>'
        sections=poker_finder.GuideText(text).sections
        self.assertEqual(sections[0]['text'],'Intro text')
        self.assertEqual(sections[1]['anchor'],'actual')
        self.assertIn('Final public text.',sections[1]['text'])
        combined=' '.join(s['text'] for s in sections)
        for token in ('secret-navigation','hidden-answer','bad script','private-hidden'):
            self.assertNotIn(token,combined)
        with self.assertRaises(ValueError):poker_finder.GuideText('<h2 id="x?bad">Bad</h2><p>text</p>')

    def test_search_covers_guide_prose_but_not_remote_article_bodies(self):
        by_url={i['url']:i for i in self.items}
        for slug in NEW:
            e=by_url['/poker/'+slug+'/']
            self.assertGreater(sum(len(s['text']) for s in e['sections']),2500)
            source=(ROOT/'_source/poker'/(slug+'.html')).read_text()
            ids={a['id'] for _,a in Page(source).elements if 'id' in a}
            for section in e['sections']:
                if section['anchor']:self.assertIn(section['anchor'],ids)
        for e in self.items:
            if e['kind']!='guide':self.assertFalse(e.get('sections'))
        e=by_url['/poker/multiway-pot-workshop/']
        self.assertTrue(any(s['anchor']=='dry-side-pot' and 'bluffed' in s['text'] for s in e['sections']))
        self.assertNotIn('data-body=',self.outputs[Path('poker/find/index.html')])

    def test_all_new_routes_have_discovery_and_accurate_scopes(self):
        for slug in NEW:
            route='/poker/'+slug+'/'
            source=(ROOT/'_source/poker'/(slug+'.html')).read_text()
            self.assertGreater(len(source.split()),500)
            self.assertEqual(source.count('class="poker-details viewer-question"'),3)
            for name in ('poker/index.html','poker/library/index.html','poker/resource-collections/index.html','sitemap.xml','poker/feed.xml'):
                self.assertIn(route,self.outputs[Path(name)])
            self.assertIn(route,check_live.targets())
            self.assertIn('fictional',source);self.assertIn('Prepared with AI assistance',source)
        for slug in ('study-calculators','resource-quality'):
            p=next(p for p in self.pages if p['path']=='/poker/'+slug+'/')
            self.assertFalse(p.get('poker_guide'))
            self.assertIn(p['path'],check_live.targets())

    def test_counterfeiting_is_recomputed_from_physical_cards(self):
        board=['3c','5d','7h','Kc','2h']; a=['As','2s','Qd','Jd']; b=['Ah','4h','Qh','Js']
        self.assertEqual(len(set(board+a+b)),13)
        def best(hole,board):
            return min(v for x in combinations(hole,2) for y in combinations(board,3) if (v:=lows(x+y)))
        self.assertEqual(best(a,board[:3]),(7,5,3,2,1))
        self.assertEqual(best(b,board[:3]),(7,5,4,3,1))
        self.assertEqual(best(a,board),(7,5,3,2,1))
        self.assertEqual(best(b,board),(5,4,3,2,1))
        self.assertEqual(best(['As','2s','4c','Jd'],board),(5,4,3,2,1))
        self.assertEqual(Fraction(1,5)+Fraction(2,5)/2+Fraction(1,5)/4,Fraction(9,20))
        self.assertFalse(any(lows(x+y) for x in combinations(a,2) for y in combinations(['2c','2d','7h','Kc','Qs'],3)))

    def test_multiway_and_lowball_worked_examples(self):
        self.assertEqual(90+30*3,180);self.assertEqual(Fraction(30,180),Fraction(1,6))
        self.assertEqual((3*50,2*(200-50)),(150,300))
        self.assertEqual(Fraction(1,2)**2,Fraction(1,4))
        self.assertGreater((7,6,4,2,1),(7,5,4,3,2))
        def badugi(hand):
            options=[]
            for n in range(1,5):
                for subset in combinations(hand,n):
                    ranks=[1 if c[0]=='A' else '23456789TJQK'.index(c[0])+2 for c in subset]
                    if len(set(ranks))==n and len({c[1] for c in subset})==n:
                        options.append((-n,*sorted(ranks,reverse=True)))
            return min(options)
        self.assertLess(badugi(['Ac','2d','3h','Ks']),badugi(['Ac','2d','3h','4h']))
        self.assertEqual(badugi(['Ac','2d','3h','4h']),(-3,3,2,1))
        self.assertEqual(high(['7s','6d','5h','4c','3s'])[0],4)

    @unittest.skipUnless(shutil.which('node'),'Node is required for client arithmetic validation')
    def test_client_calculators_against_independent_exact_fractions(self):
        inputs=[]
        for a in ('0.01','3.25','120','210','999999999'):
            for b in ('0.01','4.50','90'):
                for mode in ('call','bluff','potlimit'):inputs.append([mode,a,b,'0'])
        inputs.extend([['potlimit','500','70','80'], ['potlimit','100','0','0'], ['potlimit','100','0','10']])
        code='const m=require("./assets/poker-study-tools.js"); console.log(JSON.stringify('+json.dumps(inputs)+'.map(x=>m.calculate(...x))));'
        completed=subprocess.run(['node','-e',code],cwd=ROOT,text=True,capture_output=True,check=True)
        values=json.loads(completed.stdout)
        for row,value in zip(inputs,values):
            mode,a,b,w=row;a,b,w=map(Fraction,(a,b,w))
            if mode in ('call','bluff'):self.assertAlmostEqual(value['percent'],float(100*b/(a+b)),places=10)
            else:
                self.assertAlmostEqual(value['extra'],float(a+2*b),places=6)
                self.assertAlmostEqual(value['total'],float(w+a+2*b),places=6)
        invalid=['','-1','NaN','Infinity','1e3','1,000','1.001','1000000000','<img>']
        code='const m=require("./assets/poker-study-tools.js"); console.log(JSON.stringify('+json.dumps(invalid)+'.map(x=>{try{m.amount(x);return false;}catch(e){return true;}})));'
        self.assertTrue(all(json.loads(subprocess.run(['node','-e',code],cwd=ROOT,text=True,capture_output=True,check=True).stdout)))
        for args in [['call','0','1'],['call','100','0'],['bluff','1','0'],['potlimit','0','0','0'],['potlimit','10','1','11'],['wrong','1','2']]:
            code='const m=require("./assets/poker-study-tools.js");try{m.calculate(...'+json.dumps(args)+');process.exit(1);}catch(e){process.exit(0);}'
            self.assertEqual(subprocess.run(['node','-e',code],cwd=ROOT).returncode,0)

    def test_source_quality_counts_and_index_limits_are_generated(self):
        values=poker_quality.supplement(self.resources)
        counts=Counter(r['review_method'] for r in self.resources)
        self.assertIn(str(len(self.resources))+' unique',values['poker_review_summary'])
        self.assertIn(str(counts['index'])+' search-index',values['poker_review_summary'])
        for r in self.resources:
            if r['review_method']=='index':self.assertIn(r['id'],values['poker_review_limits'])
        r=next(r for r in self.resources if r['id']=='nj-dge-information')
        self.assertEqual(r['review_method'],'index');self.assertIn('403',r['notes'])
        r=next(r for r in self.resources if r['id']=='mit-combo-lecture')
        self.assertIn('not reviewed',r['notes'])

    def test_new_controls_preserve_network_privacy_and_page_scope(self):
        js=(ROOT/'assets/poker-study-tools.js').read_text()
        for term in ('fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage','sendBeacon','document.cookie','innerHTML','history.','location.','umami'):
            self.assertNotIn(term,js)
        for path,content in self.outputs.items():
            if path.suffix=='.html':self.assertEqual('/assets/poker-study-tools.js?v=' in content,path==Path('poker/study-calculators/index.html'))
        for name in ('poker-study-tools.js','poker-study-tools.css'):self.assertIn('/assets/'+name,check_live.targets())
        content=self.outputs[Path('poker/study-calculators/index.html')]
        self.assertNotIn('<form',content);self.assertEqual(content.count('data-tool-controls hidden'),3)
        self.assertIn('no further betting',content)
        find=self.outputs[Path('poker/find/index.html')]
        self.assertIn('download="poker-study-list.md"',find)
        self.assertIn('not included',find)

if __name__=='__main__':unittest.main(verbosity=2)
