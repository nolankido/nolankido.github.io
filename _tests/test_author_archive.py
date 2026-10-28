"""Complete native discovery with direct preservation of existing publications."""
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import author_archive
import author_archive_history as history
import beginner_history
import build
import practical_navigation_history
import visibility_sprint_history

class ArchiveParser(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.ids=[]; self.links=[]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'data-archive-id' in attrs: self.ids.append(attrs['data-archive-id'])
        if tag=='a': self.links.append(attrs.get('href'))

class AuthorArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=build.public_pages();cls.outputs=build.build_outputs()
        cls.entries=author_archive.records(cls.pages)

    def test_exactly_the_actual_articles_are_listed_once(self):
        actual=[]
        for p in self.pages:
            raw=self.outputs[build.output_path(p['path'])]
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',raw)[1])
            if schema['@type']=='Article': actual.append(p['id'])
        parser=ArchiveParser(self.outputs[Path('notes/index.html')])
        self.assertEqual(len(actual),len(self.entries))
        self.assertEqual(len(author_archive.records(visibility_sprint_history.pages(self.pages))),104)
        self.assertCountEqual(parser.ids,actual)
        self.assertEqual(len(parser.ids),len(set(parser.ids)))

    def test_all_preexisting_outputs_survive_bounded_additions(self):
        for path,digest in history.baseline()['outputs'].items():
            raw=history.before(path,self.outputs[Path(path)])
            self.assertEqual(sha256(raw.encode()).hexdigest(),digest,path)

    def test_original_article_output_and_feeds_survive_only_declared_navigation(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        for p in beginner_history.pages(self.entries):
            path=build.output_path(p['path'])
            original=practical_navigation_history.before(path,historical_outputs[path])
            self.assertEqual(sha256(original.encode()).hexdigest(),history.baseline()['outputs'][str(path)])
        for path,digest in history.baseline()['outputs'].items():
            if path.endswith('feed.xml') or path=='feed.xml': self.assertEqual(sha256(historical_outputs[Path(path)].encode()).hexdigest(),digest)

    def test_schema_order_names_and_destinations_match_the_visible_archive(self):
        raw=self.outputs[Path('notes/index.html')]
        schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',raw)[1])
        listing=schema['mainEntity'];parser=ArchiveParser(raw)
        self.assertEqual(listing['numberOfItems'],len(self.entries))
        self.assertEqual([v['position'] for v in listing['itemListElement']],list(range(1,len(self.entries)+1)))
        by_id={p['id']:p for p in self.entries}
        self.assertEqual([(v['url'],v['name']) for v in listing['itemListElement']], [('https://nolankido.com'+by_id[k]['path'],by_id[k]['title']) for k in parser.ids])
        self.assertEqual(schema['creator']['@id'],'https://nolankido.com/about/#nolan-kido')

    def test_proposals_cannot_be_mistaken_for_completed_cases(self):
        planned=[p for p in self.entries if p.get('living_well_kind')=='experiment']
        self.assertEqual(len(planned),3)
        for p in planned:self.assertEqual(author_archive.label(p),'Proposed experiment')
        recorded=[p for p in self.entries if author_archive.label(p)=='Recorded case']
        self.assertEqual({p['id'] for p in recorded}, {
            'ai-website-verification', 'local-ai-review-replies',
            'ai-book-continuity-checker', 'dinner-on-time', 'ai-weekly-reset',
            'organize-public-notes', 'local-ai-test-record',
        })

    def test_original_publication_dates_are_visible_for_every_entry(self):
        raw=self.outputs[Path('notes/index.html')]
        for p in self.entries:
            row=re.search(r'<li data-archive-id="'+re.escape(p['id'])+r'">(.*?)</li>',raw,re.S)[1]
            self.assertIn('<time datetime="'+p['date']+'">',row)
            self.assertIn('Published ',row)

    def test_archive_has_four_native_groups_and_no_new_runtime_scripts(self):
        raw=self.outputs[Path('notes/index.html')]
        self.assertEqual(raw.count('<details class="archive-group"'),4)
        old_scripts=re.findall(r'<script[^>]*src="([^"]+)"',history.before('notes/index.html',raw))
        self.assertEqual(re.findall(r'<script[^>]*src="([^"]+)"',raw),old_scripts)
        self.assertIn('href="/notes/#all-writing"',self.outputs[Path('about/index.html')])

    def test_records_do_not_mutate_input_and_exclude_utilities(self):
        before=deepcopy(self.pages);author_archive.records(self.pages)
        self.assertEqual(self.pages,before)
        self.assertTrue(all(not p.get('noindex') for p in self.entries))
        self.assertFalse(author_archive.is_article({'id':'private','noindex':True,'note':True}))

    def test_unmarked_article_change_is_not_hidden_by_predecessor_view(self):
        path='notes/trustworthy-tools/index.html'
        raw=self.outputs[Path(path)].replace('A working tool', 'A changed tool',1)
        if raw==self.outputs[Path(path)]:raw=self.outputs[Path(path)].replace('<body','<!-- changed --><body',1)
        self.assertNotEqual(sha256(history.before(path,raw).encode()).hexdigest(),history.baseline()['outputs'][path])

if __name__=='__main__':unittest.main()
