"""Feed identity, native reading controls, and unchanged public-data boundaries."""
from copy import deepcopy
from email.utils import parsedate_to_datetime
from html import escape
from pathlib import Path
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build
import follow
import poker_reading
import site_find
import check_live
from test_site import Page


def records(xml):
    return {i.findtext('link'): i for i in ET.fromstring(xml).findall('./channel/item')}


def signature(item):
    return [(c.tag, dict(c.attrib), c.text) for c in item if c.tag != 'source']


class ReadingReturnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=build.public_pages()
        cls.outputs=build.build_outputs()
        cls.combined=records(cls.outputs[follow.OUTPUT])

    def test_combined_feed_is_exact_union_with_original_records(self):
        original={}
        for path in follow.SOURCES:
            original.update(records(self.outputs[path]))
        self.assertEqual(set(self.combined),set(original))
        items=ET.fromstring(self.outputs[follow.OUTPUT]).findall('./channel/item')
        self.assertEqual(len(items),len(original))
        for url,item in self.combined.items():
            self.assertEqual(signature(item),signature(original[url]),url)
            source=item.find('source')
            self.assertIn(source.get('url'), ['https://nolankido.com/'+p.as_posix() for p in follow.SOURCES])
        self.assertNotIn('/follow/', self.combined)
        self.assertFalse(any('notebook-or-ai' in url for url in self.combined))

    def test_source_feeds_are_byte_stable(self):
        baseline=json.loads((ROOT/'_tests/entrypoints-baseline.json').read_text())['files']
        import hashlib
        for path in follow.LEGACY_SOURCES:
            self.assertEqual(hashlib.sha256(self.outputs[path].encode()).hexdigest(),baseline[str(path)])

    def test_deterministic_sort_and_required_channel_metadata(self):
        rss=ET.fromstring(self.outputs[follow.OUTPUT]);channel=rss.find('channel')
        self.assertEqual(rss.get('version'),'2.0')
        for tag in ['title','link','description','language']:
            self.assertTrue(channel.findtext(tag))
        self_link=channel.find('{'+follow.ATOM+'}link')
        self.assertEqual(self_link.get('href'),'https://nolankido.com/writing.xml')
        items=channel.findall('item')
        keys=[(-parsedate_to_datetime(i.findtext('pubDate')).timestamp(),i.findtext('link')) for i in items]
        self.assertEqual(keys,sorted(keys))
        before=deepcopy(self.outputs)
        self.assertEqual(follow.combined(dict(reversed(list(self.outputs.items()))),self.pages,'https://nolankido.com'),self.outputs[follow.OUTPUT])
        self.assertEqual(self.outputs,before)

    def mutated_source(self, mutate):
        outputs=dict(self.outputs)
        tree=ET.fromstring(outputs[Path('feed.xml')])
        mutate(tree.find('channel'))
        outputs[Path('feed.xml')]=ET.tostring(tree,encoding='unicode')
        # Derived Technology copies use the same edited canonical source.
        import practical_discovery
        config=practical_discovery.load(ROOT,self.pages)
        outputs[practical_discovery.FEED]=practical_discovery.feed(config,self.pages,outputs,'https://nolankido.com')
        return outputs

    def test_duplicate_identity_collapses_but_conflicting_copy_fails(self):
        output=self.mutated_source(lambda ch:ch.append(deepcopy(ch.find('item'))))
        self.assertEqual(len(records(follow.combined(output,self.pages,'https://nolankido.com'))),len(self.combined))
        def conflict(ch):
            item=deepcopy(ch.find('item'));item.find('title').text='Different title';ch.append(item)
        with self.assertRaisesRegex(ValueError,'Conflicting records'):
            follow.combined(self.mutated_source(conflict),self.pages,'https://nolankido.com')

    def test_reject_missing_private_proposed_and_undated_pages(self):
        for mutation in ['missing','noindex','proposed','undated']:
            pages=deepcopy(self.pages)
            target=next(p for p in pages if p['id']=='keep-the-judgment')
            if mutation=='missing':pages.remove(target)
            if mutation=='noindex':target['noindex']=True
            if mutation=='proposed':target['living_well_kind']='experiment'
            if mutation=='undated':del target['date']
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                follow.combined(self.outputs,pages,'https://nolankido.com')

    def test_reject_bad_dates_identity_and_remote_origins(self):
        cases=[('pubDate','bad date'),('pubDate','Mon, 12 Oct 2026 00:00:00 GMT'),('guid','wrong'),('link','https://other.example/private/'),('title',''),('description','')]
        for tag,value in cases:
            with self.subTest(tag=tag,value=value),self.assertRaises(ValueError):
                # Invalid identity can be rejected while deriving the Technology source.
                output=self.mutated_source(lambda ch: setattr(ch.find('item').find(tag),'text',value))
                follow.combined(output,self.pages,'https://nolankido.com')
        for origin in ['http://nolankido.com','https://nolankido.com/','https://nolankido.com?user=1']:
            with self.assertRaises(ValueError):follow.combined(self.outputs,self.pages,origin)

    def test_generated_feed_escapes_literal_text(self):
        text='<script>alert("example")</script> & an idea'
        output=self.mutated_source(lambda ch:setattr(ch.find('item').find('title'),'text',text))
        xml=follow.combined(output,self.pages,'https://nolankido.com')
        self.assertNotIn('<script>',xml)
        self.assertIn(text,[i.findtext('title') for i in ET.fromstring(xml).findall('./channel/item')])

    def test_outline_links_are_existing_body_headings(self):
        for p in self.pages:
            if not p.get('note'):continue
            raw=(ROOT/'_source'/p['source']).read_text()
            html=self.outputs[build.output_path(p['path'])]
            expected=poker_reading.section_outline(raw)
            self.assertTrue(expected)
            self.assertIn(expected,html)
            self.assertIn(raw,html)
            self.assertEqual(html.count('class="reader-outline"'),1)
            for anchor,label in poker_reading.VisibleHeadings(raw).headings:
                self.assertIn('href="#'+anchor+'"',html)
            self.assertIn('class="note-print-origin"',html)
            self.assertIn('https://nolankido.com'+p['path'],html)
            self.assertIn('Prepared with AI assistance.',html)
            self.assertIn('href="/follow/">Follow the writing',html)

    def test_follow_routes_and_no_new_script_or_signup(self):
        content=self.outputs[Path('follow/index.html')]
        links=[x.get('href') for x in Page(content).tags('a')]
        for path in ['/writing.xml','/feed.xml','/living-well/feed.xml','/poker/feed.xml','/card/','/contact/']:
            self.assertIn(path,links)
        self.assertNotIn('<form',content)
        self.assertNotIn('<input',content)
        self.assertIn('avoid receiving the same piece twice',content)
        self.assertNotIn('/follow/',[e['path'] for e in site_find.entries(ROOT,self.pages)])
        for page in self.pages:
            parsed=Page(self.outputs[build.output_path(page['path'])])
            feeds=[a['href'] for a in parsed.tags('link') if a.get('type')=='application/rss+xml']
            self.assertEqual(feeds[:2],['/writing.xml','/feed.xml'])
            self.assertIn('/follow/',[a.get('href') for a in parsed.tags('a')])
        card=self.outputs[Path('card/index.html')]
        for path in ['/start-here/','/notes/','/follow/','/nolan-kido.vcf','/card/qr.svg']:
            self.assertIn(path,card)

    def test_reading_style_is_scoped_and_export_targets_are_verified(self):
        for p in self.pages:
            self.assertEqual('/assets/reading.css' in self.outputs[build.output_path(p['path'])],bool(p.get('note') or p['id']=='follow'))
        targets=check_live.targets()
        self.assertEqual(targets['/writing.xml'],(200,self.outputs[follow.OUTPUT].encode()))
        self.assertIn('/follow/',targets)
        self.assertEqual(targets['/assets/reading.css'],(200,(ROOT/'assets/reading.css').read_bytes()))

    def test_shared_shell_changed_only_for_return_navigation(self):
        # This exact transform pins the existing analytics, contact and head configuration.
        layout=(ROOT/'_source/layout.html').read_text()
        reverted=layout.replace('  <link rel="alternate" type="application/rss+xml" title="Nolan Kido | Writing across the site" href="/writing.xml">\n','').replace('<a href="/follow/">Follow writing</a>','<a href="/feed.xml">RSS</a>')
        import hashlib
        self.assertEqual(hashlib.sha256(reverted.encode()).hexdigest(),'2c1e295caa12324de4b639701b3212358ba75a97ee72b8597a2730fd99b4d4f6')

if __name__=='__main__':unittest.main()
