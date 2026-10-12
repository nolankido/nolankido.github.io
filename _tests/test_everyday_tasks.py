"""Reader task routes, exact portable worksheets, and bounded metadata changes."""
import choice_history
from copy import deepcopy
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import everyday_tasks
import living_well
import living_well_utility as utility


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.links = []; self.feed(text)
    def handle_starttag(self, tag, attrs):
        if tag == 'a': self.links.append(dict(attrs))


class EverydayTasksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.entries = living_well.load(ROOT)
        cls.config = everyday_tasks.load(ROOT, cls.pages)
        cls.outputs = build.build_outputs()
        cls.baseline = json.loads((ROOT / '_tests/everyday-tasks-baseline.json').read_text())

    def test_exact_original_source_and_feed_preservation(self):
        for path, expected in self.baseline['files'].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256(choice_history.read(path)).hexdigest(), expected)
        self.assertEqual([{k:p.get(k) for k in ('id','path','title','date','updated','noindex')} for p in self.pages if p['id'] != 'ai-task-choice'], self.baseline['pages'])

    def test_seven_existing_tasks_and_eight_specific_search_titles(self):
        self.assertEqual(len(self.config['tasks']), 7)
        self.assertEqual(len({t['slug'] for t in self.config['tasks']}), 7)
        by_path = {p['path']: p for p in self.pages}
        for t in self.config['tasks']:
            path = '/living-well/' + t['slug'] + '/'
            page = self.outputs[build.output_path(path)]
            self.assertIn('<title>' + escape(t['seo_title']) + '</title>', page)
            self.assertIn('content="' + escape(t['description'], quote=True) + '"', page)
            self.assertEqual(by_path[path]['title'], next(e['title'] for e in self.entries if e['slug'] == t['slug']))
            self.assertIn('href="https://nolankido.com' + path + '"', page)
        hub = self.config['hub']
        self.assertEqual(by_path[hub['path']]['seo_title'], hub['seo_title'])
        self.assertEqual(by_path[hub['path']]['date'], '2026-10-10')

    def test_metadata_does_not_mutate_input_or_undated_claims(self):
        before = deepcopy(self.pages)
        output = everyday_tasks.metadata(self.pages, ROOT)
        self.assertEqual(before, self.pages)
        self.assertIsNot(output, self.pages)
        for old, new in zip(before, output):
            self.assertEqual({k:v for k,v in old.items() if k not in {'seo_title','description'}},
                             {k:v for k,v in new.items() if k not in {'seo_title','description'}})

    def test_native_routes_on_technology_and_worksheet_directory(self):
        for path in ['technology/index.html','living-well/worksheets/index.html']:
            html = self.outputs[Path(path)]
            self.assertEqual(html.count('class="everyday-task"'), 7)
            for task in self.config['tasks']:
                self.assertIn('href="/living-well/' + task['slug'] + '/"', html)
        self.assertIn('id="technology-path"', self.outputs[Path('technology/index.html')])
        self.assertIn('id="everyday-task-sheets"', self.outputs[Path('living-well/worksheets/index.html')])

    def test_exact_source_preview_download_and_live_response_inventory(self):
        sheets = utility.worksheet_exports(self.entries)
        self.assertEqual(len(sheets), 7)
        targets = check_live.targets()
        for entry in self.entries:
            if not entry.get('utility'): continue
            path = utility.worksheet_path(entry)
            self.assertEqual(sheets[path], entry['utility']['starter'])
            self.assertEqual(self.outputs[path], entry['utility']['starter'])
            self.assertEqual((ROOT / path).read_bytes(), entry['utility']['starter'].encode('utf-8'))
            self.assertEqual(targets['/' + path.as_posix()], (200, entry['utility']['starter'].encode('utf-8')))
            html = self.outputs[Path('living-well') / entry['slug'] / 'index.html']
            self.assertIn('<pre>' + escape(entry['utility']['starter']) + '</pre>', html)
            links = [a for a in Links(html).links if a.get('href') == '/' + path.as_posix()]
            self.assertEqual(len(links), 2)
            self.assertTrue(all('download' in a for a in links))
            self.assertIn('href="/technology/#technology-path"', html)
        self.assertEqual(len(living_well.worksheet_exports()), 5)

    def test_no_new_runtime_dependency_and_existing_gallery_kept(self):
        css = (ROOT / 'assets/everyday-tasks.css').read_text()
        self.assertLess(len(css), 2400)
        self.assertNotIn('@import', css)
        self.assertNotIn('url(', css)
        tech = self.outputs[Path('technology/index.html')]
        self.assertEqual(tech.count('class="work-preview"'), 2)
        self.assertIn('aria-labelledby="working-examples"', tech)
        self.assertNotIn('fetch(', tech)
        for task in self.config['tasks']:
            page = self.outputs[Path('living-well') / task['slug'] / 'index.html']
            self.assertNotIn('<form', page)
            self.assertNotIn('localStorage', page)
            self.assertIn('No generative AI required', page)

    def test_invalid_config_rejected(self):
        mutations = []
        c=deepcopy(self.config);c['tasks']=[];mutations.append(c)
        c=deepcopy(self.config);c['tasks'].append(c['tasks'][0]);mutations.append(c)
        c=deepcopy(self.config);c['tasks'][0]['slug']='../outside';mutations.append(c)
        c=deepcopy(self.config);c['tasks'][0]['slug']='does-not-exist';mutations.append(c)
        c=deepcopy(self.config);c['tasks'][0]['description']='';mutations.append(c)
        c=deepcopy(self.config);c['tasks'][0]['seo_title']=None;mutations.append(c)
        c=deepcopy(self.config);c['hub']['path']='https://example.com/';mutations.append(c)
        with TemporaryDirectory() as d:
            root=Path(d);(root/'_source').mkdir()
            for c in mutations:
                (root/'_source/everyday-tasks.json').write_text(json.dumps(c))
                with self.assertRaises(ValueError):everyday_tasks.load(root, self.pages)
        pages=deepcopy(self.pages)
        next(p for p in pages if p['path']=='/living-well/scattered-notes-to-next-step/')['noindex']=True
        with self.assertRaises(ValueError):everyday_tasks.load(ROOT, pages)

    def test_untrusted_labels_and_worksheet_text_are_escaped(self):
        config=deepcopy(self.config)
        config['tasks'][0]['label']='<img src=x onerror=alert(1)>'
        html=everyday_tasks.cards(config,self.entries)
        self.assertNotIn('<img src=x', html)
        self.assertIn('&lt;img', html)
        entry=deepcopy(next(e for e in self.entries if e.get('utility')))
        entry['utility']['starter']='<script>bad</script> & literal text'
        self.assertIn('&lt;script&gt;bad&lt;/script&gt;', utility.starter(entry))
        entry['slug']='../../outside'
        with self.assertRaises(ValueError):utility.worksheet_path(entry)
        with self.assertRaises(ValueError):utility.worksheet_exports([self.entries[0],entry])
        original=next(e for e in self.entries if e.get('utility'))
        with self.assertRaises(ValueError):utility.worksheet_exports([original,original])

    def test_missing_worksheet_fails_instead_of_broken_promise(self):
        entries=deepcopy(self.entries)
        next(e for e in entries if e['slug']==self.config['tasks'][0]['slug']).pop('utility')
        with self.assertRaises(ValueError):everyday_tasks.cards(self.config,entries)

if __name__=='__main__':unittest.main(verbosity=2)
