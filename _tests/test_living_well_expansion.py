"""Expanded free readings: discoverability, honest formats, sources and preserved scope."""
from copy import deepcopy
from html import escape
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build
import living_well as lw

class ExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.new=json.loads((ROOT/'_source/living-well/expansion.json').read_text())['entries']
        cls.entries={e['slug']:e for e in lw.load(ROOT)}
        cls.outputs=build.build_outputs()

    def test_five_distinct_readings_and_no_fabricated_field_note(self):
        self.assertEqual(len(self.new),5)
        self.assertEqual(len(lw.manifest(ROOT)),53)
        self.assertEqual({e['format'] for e in self.new if e.get('format')}, {'practice-path','short-read'})
        for e in self.new:
            self.assertNotEqual(e['kind'],'experiment')
            self.assertEqual(e['published'],'2026-10-09')
            self.assertNotIn('updated',e)
            self.assertEqual(len(e['related']),2)
            body=self.outputs[Path('living-well')/e['slug']/'index.html']
            self.assertIn('Prepared with AI assistance',body)
            self.assertIn('not accounts of Nolan',body)
        field=self.outputs[Path('living-well/field-notes/index.html')]
        self.assertIn('No completed personal field notes are published here yet',field)

    def test_formats_have_clear_reader_routes(self):
        ideas=self.outputs[Path('living-well/ideas/index.html')]
        guides=self.outputs[Path('living-well/guides/index.html')]
        home=self.outputs[Path('living-well/index.html')]
        self.assertIn('id="short-reads"',ideas)
        self.assertIn('Short read',ideas)
        self.assertIn('id="free-practice-paths"',guides)
        self.assertIn('Free practice path',guides)
        for slug in ['consciousness-which-question','read-a-poem-without-a-lesson','meditation-without-buying-a-lifestyle','learning-with-ai-without-skipping-understanding']:
            self.assertIn('href="/living-well/'+slug+'/"',home)
        self.assertEqual(sum(e.get('format')=='short-read' for e in self.new),1)
        for e in self.new:
            subject=self.outputs[Path('living-well/topics')/e['topic']/'index.html']
            self.assertIn('href="/living-well/'+e['slug']+'/"',subject)

    def test_sources_are_linked_with_scope_and_outline(self):
        for e in self.new:
            body=self.outputs[Path('living-well')/e['slug']/'index.html']
            if not e.get('sources'):
                self.assertNotIn('id="sources-and-context"',body)
                continue
            self.assertEqual(body.count('id="sources-and-context"'),1)
            self.assertIn('href="#sources-and-context"',body)
            for s in e['sources']:
                self.assertIn('href="'+escape(s['url'],quote=True)+'"',body)
                self.assertIn(escape(s['note']),body)
                self.assertEqual(s['checked'],'2026-10-09')
        guide=self.entries['learning-with-ai-without-skipping-understanding']
        text=json.dumps(guide)
        self.assertIn('not a real event',text)
        self.assertIn('report of what a particular AI system returned',text)
        note=json.dumps(self.entries['read-a-poem-without-a-lesson'])
        self.assertIn('No verse is reproduced',note)

    def test_source_notes_escape_text(self):
        e={'sources':[{'label':'<b>Title</b>','note':'<img src=x onerror=alert(1)>','url':'https://example.com/','checked':'2026-10-09'}]}
        notes=lw.source_notes(e)
        self.assertIn('&lt;b&gt;Title&lt;/b&gt;',notes)
        self.assertNotIn('<img',notes)
        self.assertIn('&lt;img',notes)

    def test_invalid_source_or_format_is_rejected(self):
        changes=[lambda e:e['sources'][0].update(url='javascript:alert(1)'),
                 lambda e:e['sources'][0].update(url='https://name:pass@example.com/'),
                 lambda e:e['sources'][0].update(checked='invalid'),
                 lambda e:e['sources'][0].update(note=''),
                 lambda e:e.update(sources='not-a-list'),
                 lambda e:e.update(format='paid-course'),
                 lambda e:e.update(format='short-read')]
        for change in changes:
            with self.subTest(change=change),tempfile.TemporaryDirectory() as td:
                root=Path(td)
                shutil.copytree(ROOT/'_source/living-well',root/'_source/living-well')
                data={'entries':deepcopy(self.new)}
                change(data['entries'][0])
                (root/'_source/living-well/expansion.json').write_text(json.dumps(data))
                with self.assertRaises(ValueError):lw.load(root)

    def test_revisions_keep_dates_and_old_anchors(self):
        for slug,count in [('two-good-lives',6),('quiet-morning',5)]:
            e=self.entries[slug]
            self.assertEqual(e['published'],'2026-10-08')
            self.assertEqual(e['updated'],'2026-10-09')
            self.assertTrue(e['revision'])
            body=self.outputs[Path('living-well')/slug/'index.html']
            for number in range(1,count+1):self.assertIn('id="part-'+str(number)+'"',body)
            self.assertIn('id="part-'+str(count+1)+'"',body)
        feed=ET.fromstring(self.outputs[Path('living-well/feed.xml')])
        self.assertEqual(len(feed.findall('./channel/item')),23)

if __name__=='__main__':unittest.main(verbosity=2)
