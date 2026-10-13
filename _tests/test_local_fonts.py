"""Exact font provenance and independent preservation of the production release."""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import copy,json,re,shutil,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,check_live,font_delivery
import local_fonts_history as history
import search_sections_history

class LocalFontsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs={p:search_sections_history.before(p,data) for p,data in build.build_outputs().items()};cls.pages=build.public_pages();cls.baseline=history.baseline()
        cls.record=json.loads((ROOT/font_delivery.LOCAL_PROVENANCE).read_text())

    def test_only_reviewed_head_and_privacy_changes_survive_against_production(self):
        self.assertEqual(len(self.baseline['outputs']),198)
        self.assertEqual(set(map(str,self.outputs)),set(self.baseline['outputs']))
        self.assertEqual(history.pages(self.pages),self.baseline['pages'])
        unchanged_bodies=0
        for p,text in self.outputs.items():
            restored=history.before(p,text)
            self.assertEqual(sha256(restored.encode()).hexdigest(),self.baseline['outputs'][str(p)],str(p))
            if p.suffix=='.html' and str(p)!='privacy/index.html':
                self.assertEqual(text.split('<body',1)[1],restored.split('<body',1)[1]);unchanged_bodies+=1
        self.assertEqual(unchanged_bodies,170)

    def test_every_original_file_and_the_exact_new_asset_inventory_are_checked(self):
        self.assertEqual(len(self.baseline['files']),316)
        paths={p.relative_to(ROOT).as_posix() for d in ['_source','assets','downloads'] for p in (ROOT/d).rglob('*') if p.is_file()}
        self.assertEqual(paths,set(self.baseline['files'])|set(history.change()['new_files']))
        changed=[]
        for p,digest in self.baseline['files'].items():
            raw=search_sections_history.before(p,(ROOT/p).read_bytes())
            if sha256(raw).hexdigest()!=digest:changed.append(p)
            self.assertEqual(sha256(history.before(p,raw)).hexdigest(),digest,p)
        self.assertCountEqual(changed,['_source/privacy.html','_source/pages.json','assets/site-fonts.css'])

    def test_all_38_faces_and_24_files_preserve_descriptors_and_unicode_coverage(self):
        source=font_delivery.declarations(ROOT);local=font_delivery.local_declarations(ROOT)
        self.assertEqual(history.before('assets/site-fonts.css',local),source)
        self.assertEqual(len(re.findall('@font-face',local)),38)
        self.assertNotIn('https:',local)
        self.assertEqual(set(re.findall(r'url\(([^)]+)\)',local)),{'/'+p['path'] for p in self.record['files']})
        self.assertEqual((len(self.record['files']),len(self.record['licenses'])),(24,3))
        self.assertEqual(sum(p['bytes'] for p in self.record['files']),422284)
        self.assertEqual(set(history.change()['new_files']),{p['path'] for p in font_delivery.local_files(ROOT)})

    def test_missing_corrupt_unmapped_or_unlicensed_fonts_fail_closed(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            for p in [font_delivery.SOURCE,font_delivery.PROVENANCE,font_delivery.LOCAL_PROVENANCE]+[Path(x['path']) for x in self.record['files']+self.record['licenses']]:
                (root/p).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,root/p)
            first=root/self.record['files'][0]['path'];original=first.read_bytes();first.write_bytes(original+b'x')
            with self.assertRaises(ValueError):font_delivery.local_declarations(root)
            first.write_bytes(original)
            for key in ['files','licenses']:
                record=copy.deepcopy(self.record);record[key].pop();(root/font_delivery.LOCAL_PROVENANCE).write_text(json.dumps(record))
                with self.assertRaises(ValueError):font_delivery.local_declarations(root)
            record=copy.deepcopy(self.record);record['files'][0]['path']='../other.woff2';(root/font_delivery.LOCAL_PROVENANCE).write_text(json.dumps(record))
            with self.assertRaises(ValueError):font_delivery.local_declarations(root)

    def test_all_pages_use_only_local_font_delivery_and_live_check_covers_each_file(self):
        css=font_delivery.local_declarations(ROOT)
        for p,text in self.outputs.items():
            if p.suffix!='.html':continue
            self.assertEqual(text.count('href="'+font_delivery.href(css)+'"'),1)
            self.assertNotIn('fonts.gstatic.com',text);self.assertNotIn('fonts.googleapis.com',text)
        targets=check_live.targets()
        for p in history.change()['new_files']:self.assertEqual(targets['/'+p],(200,(ROOT/p).read_bytes()))
        self.assertEqual(len(targets),399)
        privacy=self.outputs[Path('privacy/index.html')]
        self.assertIn(history.change()['privacy_new'],privacy)
        self.assertIn('Updated October 13, 2026',privacy)
        self.assertIn('"dateModified": "2026-10-13"',privacy)

    def test_history_does_not_hide_other_html_privacy_css_or_metadata_changes(self):
        for path,old,new in [('about/index.html','<body','<!-- unreviewed --><body'),('privacy/index.html','Umami Cloud','Other Analytics'),('assets/site-fonts.css','font-display: swap','font-display: block')]:
            changed=self.outputs[Path(path)].replace(old,new,1)
            self.assertNotEqual(changed,self.outputs[Path(path)])
            self.assertNotEqual(sha256(history.before(path,changed).encode()).hexdigest(),self.baseline['outputs'][path])
        changed=copy.deepcopy(self.pages);next(p for p in changed if p['id']=='privacy')['description']='Unreviewed'
        self.assertNotEqual(history.pages(changed),self.baseline['pages'])
        self.assertEqual(history.before('unrelated.html',self.outputs[Path('index.html')]),self.outputs[Path('index.html')])

if __name__=='__main__':unittest.main()
