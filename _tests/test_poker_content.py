"""Public catalog and baseline contracts. All invented records stay in temp files."""
from contextlib import contextmanager
from copy import deepcopy
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from xml.etree import ElementTree as ET
import hashlib
import json
import shutil
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import poker_content as pc
import poker_draft


def fixture(kind='episode', slug='test-episode'):
    entry = {'kind':kind, 'slug':slug, 'title':'Synthetic test only', 'summary':'Not a real episode or public account.',
             'published':'2026-10-05', 'approved':True,
             'sections':[{'heading':'Recorded action', 'paragraphs':['Fictional test text.']},
                         {'heading':'Thinking then', 'paragraphs':['A test interpretation.']},
                         {'heading':'Review now', 'paragraphs':['More test text.']}],
             'spoiler':['Synthetic result, not a real result.']}
    if kind=='episode':
        entry.update(video_url='https://www.youtube.com/watch?v=abcdefghijk', duration_seconds=900,
                     chapters=[{'seconds':0,'title':'Opening'},{'seconds':150,'title':'A decision'}])
    if kind=='hand':
        entry['record_type']='illustrative'
    return entry

@contextmanager
def catalog_root(entries):
    with TemporaryDirectory() as d:
        root=Path(d)
        shutil.copytree(ROOT, root, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git','__pycache__'))
        (root/'_source/poker/catalog.json').write_text(json.dumps({'version':1,'entries':entries}))
        yield root

class PokerContentTests(unittest.TestCase):
    def test_empty_catalog_has_real_reader_paths(self):
        result=build.build_outputs()[Path('poker/index.html')]
        if not pc.load(ROOT)['entries']:
            self.assertIn('No vlog episodes or tournament stories are published on this site yet.',result)
        for route in ['/poker/start-here/','/poker/study/','/poker/reviewing-a-hand/','/poker/feed.xml']:
            self.assertIn(route,result)
        self.assertNotIn('<iframe',result)

    def test_episode_generates_every_discovery_path(self):
        e=fixture(); h=fixture('hand','test-hand'); s=fixture('story','test-story')
        e['related']=['test-hand']
        with catalog_root([e,h,s]) as root, patch.object(build,'ROOT',root), patch.object(build,'SOURCE',root/'_source'):
            outputs=build.build_outputs(); data=pc.load(root)
            for entry in data['entries']:
                path=pc.route(entry)
                self.assertIn(build.output_path(path),outputs)
                for index in ['poker/index.html','sitemap.xml','poker/feed.xml']:
                    self.assertIn(path, outputs[Path(index)])
            episode=outputs[Path('poker/episodes/test-episode/index.html')]
            self.assertIn('v=abcdefghijk&amp;t=150s',episode)
            self.assertIn('Result and later review (spoilers)',episode)
            self.assertNotIn('<details class="poker-details" open',episode)
            self.assertIn('/poker/hands/test-hand/',episode)
            self.assertIn('/poker/episodes/test-episode/',outputs[Path('poker/hands/test-hand/index.html')])
            self.assertEqual(outputs[Path('index.html')],(ROOT/'index.html').read_text())
            self.assertEqual(outputs,build.build_outputs())
            self.assertIn('"@type": "Article"',episode)
            self.assertIn('property="article:published_time"',episode)
            self.assertIn('href="https://nolankido.com/poker/episodes/test-episode/"',episode)
            self.assertNotIn('test-episode',outputs[Path('feed.xml')])

    def test_shared_tests_and_live_targets_see_generated_records(self):
        e=fixture()
        with catalog_root([e]) as root, patch.object(build,'ROOT',root), patch.object(build,'SOURCE',root/'_source'):
            for path,content in build.build_outputs().items():
                file=root/path; file.parent.mkdir(parents=True,exist_ok=True); file.write_text(content)
            import check_live
            self.assertIn(pc.route(e),check_live.targets(root))
            self.assertEqual(len(build.public_pages()),len(json.loads((root/'_source/pages.json').read_text()))+len(build.poker_topics.manifest(root))+len(build.living_well.manifest(root))+1)

    def test_text_is_escaped_not_executed(self):
        e=fixture(); e['sections'][0]['paragraphs']=['<script>alert("test")</script>']
        with catalog_root([e]) as root:
            rendered=pc.render(e,pc.load(root))
            self.assertIn('&lt;script&gt;',rendered)
            self.assertNotIn('<script>',rendered)

    def test_external_url_is_normalized_without_tracking(self):
        e=fixture(); e['video_url']='https://youtu.be/abcdefghijk?si=unwanted&t=5'
        self.assertEqual(pc.video_link(e),'https://www.youtube.com/watch?v=abcdefghijk')
        for bad in ['http://youtu.be/abcdefghijk','https://www.youtube.com.evil.test/watch?v=abcdefghijk',
                    'https://evil.test/abcdefghijk','javascript:alert(1)','https://user:pass@youtu.be/abcdefghijk',
                    'https://youtu.be/short','https://youtube.com/watch?v=abcdefghijk&v=lmnopqrstuv']:
            with self.subTest(url=bad), self.assertRaises(ValueError): pc.youtube_id(bad)

    def test_invalid_catalog_records_fail_closed(self):
        variants=[]
        def change(key,value):
            e=fixture(); e[key]=value; variants.append(e)
        change('approved',False); change('approved',1); change('slug','../private')
        change('kind','unknown'); change('published','2026-02-30')
        change('title',''); change('private_notes','must not be in this schema')
        change('related',['missing']); change('related',['test-episode'])
        change('chapters',[{'seconds':4,'title':'No zero'}])
        change('chapters',[{'seconds':0,'title':'Start'},{'seconds':900,'title':'Too late'}])
        change('chapters',[{'seconds':False,'title':'Boolean'}])
        change('chapters',[{'seconds':0,'title':'Start'},{'seconds':0,'title':'Duplicate'}])
        change('updated','2026-10-04'); change('revision','No update date')
        change('video_url','https://untrusted.test/video')
        change('duration_seconds',False)
        change('image',{'src':'/assets/poker/../private.jpg','alt':'No','width':100,'height':100})
        change('image',{'src':'/assets/poker/missing.jpg','alt':'No','width':100,'height':100})
        change('sources',[{'label':'Unsafe','url':'javascript:alert(1)'}])
        for e in variants:
            with self.subTest(entry=e), catalog_root([e]) as root, self.assertRaises(ValueError): pc.load(root)
        e=fixture('hand','bad-hand'); e.pop('record_type')
        with catalog_root([e]) as root, self.assertRaises(ValueError): pc.load(root)
        with catalog_root([fixture(),fixture()]) as root, self.assertRaises(ValueError): pc.load(root)

    def test_publication_dates_cannot_schedule_future_content(self):
        as_of = date(2026, 10, 7)

        future = fixture('story', 'future-story')
        future['published'] = '2026-10-08'
        with catalog_root([future]) as root, self.assertRaisesRegex(
                ValueError, 'Publication date cannot be in the future'):
            pc.load(root, as_of=as_of)

        today = fixture('story', 'today-story')
        today['published'] = '2026-10-07'
        with catalog_root([today]) as root:
            self.assertEqual(pc.load(root, as_of=as_of)['entries'][0]['published'], '2026-10-07')

        future_update = fixture('story', 'future-update')
        future_update.update(updated='2026-10-08', revision='Synthetic correction.')
        with catalog_root([future_update]) as root, self.assertRaisesRegex(
                ValueError, 'Update date cannot be in the future'):
            pc.load(root, as_of=as_of)

        today_update = fixture('story', 'today-update')
        today_update.update(updated='2026-10-07', revision='Synthetic correction.')
        with catalog_root([today_update]) as root:
            self.assertEqual(pc.load(root, as_of=as_of)['entries'][0]['updated'], '2026-10-07')

        with catalog_root([today]) as root, self.assertRaises(TypeError):
            pc.load(root, as_of='2026-10-07')

    def test_more_than_six_entries_stay_reachable(self):
        entries=[fixture('story','test-'+str(i)) for i in range(9)]
        with catalog_root(entries) as root:
            result=pc.supplement(pc.load(root),root)['poker_collection']
            self.assertIn('Earlier stories and episodes',result)
            for e in entries: self.assertIn(pc.route(e),result)

    def test_revision_and_feed_use_explicit_dates(self):
        e=fixture(); e.update(updated='2026-10-06',revision='A clearly described correction.')
        with catalog_root([e]) as root:
            data=pc.load(root); result=pc.render(e,data)
            self.assertIn('Updated 2026-10-06',result)
            feed=ET.fromstring(pc.feed(pc.manifest(data),'https://nolankido.com'))
            self.assertIn('05 Oct 2026',feed.findtext('./channel/item/pubDate'))

    def test_draft_helper_refuses_public_paths_and_overwriting(self):
        with TemporaryDirectory() as d:
            root=Path(d)/'site'; root.mkdir()
            with self.assertRaises(ValueError): poker_draft.create('episode','draft',root/'draft.json',root)
            output=Path(d)/'private/draft.json'
            poker_draft.create('episode','draft',output,root)
            self.assertIs(json.loads(output.read_text())['approved'],False)
            with self.assertRaises(FileExistsError): poker_draft.create('episode','draft',output,root)

    def test_study_previews_match_the_downloads(self):
        from html import unescape
        import re
        html=build.build_outputs()[Path('poker/study/index.html')]
        previews=[unescape(x) for x in re.findall(r'<pre>(.*?)</pre>',html,re.S)]
        self.assertEqual(previews,[(ROOT/'downloads'/name).read_text() for name in ['poker-hand-review.md','poker-session-debrief.md']])
        self.assertNotIn('<form',html)

    def test_orphaned_generated_article_blocks_release(self):
        import subprocess
        with catalog_root([]) as root:
            file=root/'poker/episodes/removed/index.html';file.parent.mkdir(parents=True)
            file.write_text(build.MARKER+'<h1>Old content</h1>')
            result=subprocess.run([sys.executable,str(root/'_scripts/build.py')],cwd=root,capture_output=True,text=True)
            self.assertEqual(result.returncode,1)
            self.assertIn('Orphaned poker page',result.stderr)

    def test_home_and_nonpoker_baseline_are_unchanged(self):
        # Deliberate homepage redesigns must explicitly review this contract.
        paths = BASELINE_PATHS
        digester=hashlib.sha256()
        for path in paths:
            digester.update(path.encode()+b'\0'+(ROOT/path).read_bytes()+b'\0')
        self.assertEqual(digester.hexdigest(),BASELINE_DIGEST)
        self.assertNotIn('/assets/poker.css',build.build_outputs()[Path('index.html')])

BASELINE_PATHS = ['404.html', 'CNAME', '_source/home.html', '_source/layout.html', '_source/site.json', 'about/index.html', 'assets/contact.js', 'assets/hubs.css', 'assets/site.css', 'bio/index.html', 'card/index.html', 'contact/index.html', 'creative/index.html', 'feed.xml', 'index.html', 'notes/decision-quality/index.html', 'notes/finishing-is-a-decision/index.html', 'notes/generous-explanations/index.html', 'notes/index.html', 'notes/learning-from-the-beginning/index.html', 'notes/trustworthy-tools/index.html', 'privacy/index.html', 'resources/index.html', 'styles.css', 'technology/index.html']
# October 9: reviewed owner-approved public introductions and bios include Living Well.
# All other source and protected contact, privacy, design and Poker checks remain independent.
BASELINE_DIGEST = 'ad2792feea97faaba1cf540801ec4d1cc13beca7199af60a5bf8c474ba3ad3aa'

if __name__=='__main__': unittest.main(verbosity=2)
