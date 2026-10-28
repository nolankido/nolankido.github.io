"""Search readiness must describe the real site without manufacturing authority."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'_scripts'))
import build
import check_search
import entrypoints
import follow
import poker_content
import presentation
import search_visibility as search
import visibility_discovery_history


class SearchVisibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.site = json.loads((ROOT/'_source/site.json').read_text())
        cls.report = check_search.audit(ROOT, cls.pages, cls.site['url'])
        cls.outputs = build.build_outputs()
        cls.presentation = presentation.load(ROOT, cls.pages)

    def test_entire_committed_site_passes_search_contract(self):
        self.assertEqual(self.report['errors'], [])
        self.assertEqual(self.report['status'], 'pass')
        self.assertEqual(self.report['pages'], len(self.pages))
        self.assertEqual(self.report, json.loads((ROOT/'_reports/search-audit.json').read_text()))
        self.assertEqual(self.report['unique_titles'], len(self.pages))
        self.assertEqual(self.report['unique_descriptions'], len(self.pages))
        self.assertEqual(self.report['breadcrumb_pages'], len(self.pages)-2)
        self.assertEqual(self.report['noindex_pages'], 5)

    def test_policy_is_an_explicit_copy_not_a_catalog_mutation(self):
        raw = [{'id':'home','path':'/'},{'id':'find','path':'/find/'},
               {'id':'404','path':'/404.html','noindex':True}]
        before = deepcopy(raw)
        result = search.apply_policy(raw)
        self.assertEqual(raw, before)
        self.assertTrue(result[1]['noindex'])
        self.assertTrue(result[2]['noindex'])
        self.assertNotIn('noindex', result[0])
        self.assertEqual({p['id'] for p in self.pages if p.get('noindex')}, search.UTILITY_IDS | {'404'})

    def test_noindex_does_not_break_public_reader_routes(self):
        config = entrypoints.load(ROOT, self.pages)
        rendered = entrypoints.interest_cards(config, self.pages)
        self.assertIn('href="/poker/find/"', rendered)
        find = self.outputs[Path('poker/find/index.html')]
        self.assertIn('noindex', find)
        self.assertIn('/assets/poker-finder.js', find)
        self.assertIn('href="/poker/library/"', find)
        self.assertNotIn('Disallow:', (ROOT/'robots.txt').read_text())

    def test_utility_change_keeps_legacy_feeds_byte_stable(self):
        for route in ['feed.xml','poker/feed.xml','living-well/feed.xml','writing.xml']:
            self.assertEqual(self.outputs[Path(route)], (ROOT/route).read_text())
        items = ET.fromstring(self.outputs[Path('poker/feed.xml')]).findall('./channel/item')
        self.assertEqual(sum(item.findtext('link')=='https://nolankido.com/poker/find/' for item in items), 1)
        pages = deepcopy(self.pages)
        next(p for p in pages if p['id']=='keep-the-judgment')['noindex'] = True
        with self.assertRaises(ValueError):
            follow.combined(self.outputs, pages, self.site['url'])
        hidden = {'id':'new-hidden','path':'/poker/new-hidden/','date':'2026-10-11','noindex':True,
                  'title':'Do not publish','description':'Not an RSS record'}
        self.assertNotIn('/poker/new-hidden/', poker_content.feed(self.pages+[hidden], self.site['url']))
        self.assertEqual(search.LEGACY_FEED_IDS, {'poker-find'})

    def test_profile_and_articles_share_identity_without_claim_inflation(self):
        for p in self.pages:
            doc = check_search.Document(self.outputs[build.output_path(p['path'])])
            schema = doc.schemas[0]
            if schema['@type']=='Article':
                self.assertEqual(schema['author']['@id'], 'https://nolankido.com/about/#nolan-kido')
                self.assertNotEqual(schema['@id'],schema['mainEntityOfPage']['@id'])
                self.assertEqual(schema['mainEntityOfPage']['url'],schema['url'])
                self.assertNotIn('breadcrumb',schema)
                if p.get('note'):
                    self.assertNotIn('class="search-author"',self.outputs[build.output_path(p['path'])])
        about = check_search.Document(self.outputs[Path('about/index.html')]).schemas[0]
        self.assertEqual(set(about['mainEntity']), {'@type','@id','name','url','description','sameAs'})
        self.assertEqual(about['mainEntity']['sameAs'], ['https://github.com/nolankido', 'https://dev.to/kidon'])
        self.assertEqual(about['mainEntity']['description'], self.site['bio_short'])
        self.assertEqual(about['@type'],'ProfilePage')

    def test_existing_breadcrumb_is_not_replaced_or_duplicated(self):
        p={'id':'deep','path':'/technology/deep/','title':'A < B & C'}
        pages=[{'id':'home','path':'/','title':'Home'},{'id':'technology','path':'/technology/','title':'Technology'},p]
        old='<nav aria-label="Breadcrumb"><a href="/">Home</a><a href="/technology/">Tech <em>&amp; life</em></a><span>A &lt; B &amp; C</span></nav><section>Header</section>'
        header, trail=search.breadcrumb(p,pages,old)
        self.assertEqual(header,old)
        self.assertEqual(trail,[('/','Home'),('/technology/','Tech & life'),('/technology/deep/','A < B & C')])
        new, trail=search.breadcrumb(p,pages,'<section>Header</section>')
        self.assertEqual(new.count('aria-label="Breadcrumb"'),1)
        self.assertIn('A &lt; B &amp; C',new)
        self.assertNotIn('A < B',new)
        with self.assertRaises(ValueError):
            search.breadcrumb(p,pages,'<nav aria-label="Breadcrumb"><a href="/missing/">Missing</a></nav>')

    def test_decorator_copies_inputs_and_rejects_noncanonical_origins(self):
        page=next(p for p in self.pages if p['id']=='technology')
        schema={'@context':'https://schema.org','@type':'WebPage','url':self.site['url']+page['path']}
        before=deepcopy(schema)
        result,_=search.decorate(page,self.pages,self.site,schema,'<section>Header</section>',self.presentation)
        self.assertEqual(schema,before)
        self.assertEqual(result['@type'],'CollectionPage')
        for origin in ['http://nolankido.com','https://nolankido.com/','https://nolankido.com?q=x','https://nolankido.com/#x']:
            site={**self.site,'url':origin}
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                search.decorate(page,self.pages,site,schema,'',self.presentation)

    def test_generic_brand_art_is_not_misrepresented_as_an_article_illustration(self):
        actual_images = {
            'ai-book-continuity-checker': ('/assets/projects/preflight-holmes-report.png', 1200, 1349),
            'dinner-on-time': ('/assets/projects/dinner-on-time-preview.jpg', 2400, 1396),
        }
        seen = set()
        for p in self.pages:
            document=check_search.Document(self.outputs[build.output_path(p['path'])])
            schema=document.schemas[0]
            if schema['@type']=='Article':
                if p['id'] in actual_images:
                    path, width, height = actual_images[p['id']]
                    image = schema['image']
                    self.assertEqual(image['@type'], 'ImageObject')
                    self.assertEqual(image['url'], self.site['url'] + path)
                    self.assertEqual((image['width'], image['height']), (width, height))
                    visible = [tag for tag in document.tags('img') if tag.get('src') == path]
                    self.assertEqual(len(visible), 1)
                    self.assertEqual((visible[0].get('width'), visible[0].get('height')), (str(width), str(height)))
                    self.assertTrue((ROOT / path.lstrip('/')).is_file())
                    seen.add(p['id'])
                else:
                    self.assertNotIn('image', schema)
        self.assertEqual(seen, set(actual_images))
        for key in ['technology','task-brief']:
            self.assertIn(key,self.presentation['pages'])
        app=check_search.Document(self.outputs[Path('technology/task-brief/index.html')]).schemas[0]['mainEntity']
        self.assertEqual(app['@type'],'WebApplication')
        self.assertTrue(app['isAccessibleForFree'])
        self.assertNotIn('offers',app)
        self.assertNotIn('aggregateRating',app)

    def test_new_evidence_routes_reuse_real_work(self):
        tech=self.outputs[Path('technology/index.html')]
        about=self.outputs[Path('about/index.html')]
        tool=self.outputs[Path('technology/task-brief/index.html')]
        for path in ['/technology/task-brief/#how-it-works','/notes/trustworthy-tools/','/living-well/did-the-tool-actually-help/']:
            self.assertIn('href="'+path+'"',tech)
            self.assertIn('href="'+path+'"',about)
        self.assertIn('id="try-the-work"',about)
        for anchor in ['how-it-works','brief-design','brief-checks','brief-data-boundary','brief-outcome']:
            self.assertIn('id="'+anchor+'"',tool)
        self.assertIn('web fonts',tool)
        self.assertIn('analytics',tool)
        self.assertIn('No AI runs here.',tool)
        self.assertIn('No personal results',tool)
        self.assertNotIn('measured productivity gain',tool.lower().replace('not a measured productivity gain',''))

    def test_original_about_prose_is_preserved_beside_the_new_work_links(self):
        source=visibility_discovery_history.before('_source/about.html',(ROOT/'_source/about.html').read_text())
        public_links='<p class="small-copy" id="public-work-profiles">You can also explore ${public_work_profiles}.</p>\n'
        self.assertEqual(source.count(public_links), 1)
        source=source.replace(public_links, '', 1)
        prior=re.sub(r'<h2 id="try-the-work">.*?(?=<h2>)','',source,flags=re.S)
        revised='<p class="intro"><strong>AI Works Human Decides</strong> is how I think about putting AI to use in everyday life and small-business work. Let the technology help with a defined task. Keep the purpose, the checks, and the consequential decisions with people.</p>'
        previous='<p class="intro">I like making things useful, understanding difficult ideas, and leaving room for a life beyond the work.</p>'
        self.assertEqual(prior.count(revised), 1)
        prior=prior.replace(revised, previous, 1)
        self.assertEqual(hashlib.sha256(prior.encode()).hexdigest(),
                         '913c479a365ef5029686c0972d9c985dbe847ff3aa10d63951c7e5c9ba536909')

    def test_audit_fails_on_real_output_tampering(self):
        page=next(p for p in self.pages if p['id']=='home')
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://nolankido.com/</loc></url></urlset>')
            raw=self.outputs[Path('index.html')]
            changed=raw.replace('rel="canonical" href="https://nolankido.com/"','rel="canonical" href="https://example.com/"')
            (root/'index.html').write_text(changed)
            report=check_search.audit(root,[page],self.site['url'])
            self.assertEqual(report['status'],'fail')
            self.assertTrue(any('canonical' in e for e in report['errors']))

if __name__=='__main__':unittest.main()
