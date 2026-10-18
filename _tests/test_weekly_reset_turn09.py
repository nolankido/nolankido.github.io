"""Small private-use weekly reset and worksheet parity regressions."""
from html import escape
from pathlib import Path
import sys, unittest, json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build, living_well

class WeeklyResetTurn09Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=build.build_outputs()
        cls.page=cls.outputs[Path('living-well/weekly-reset/index.html')]
        cls.entry=next(e for e in living_well.load(ROOT) if e['slug']=='weekly-reset')
    def test_early_small_start_has_one_action_and_room(self):
        self.assertIn('The small version: three moves, then stop',self.page)
        self.assertLess(self.page.index('The small version: three moves, then stop'),self.page.index('id="part-1"'))
        for word in ('Check:','Choose:','Release:'):
            self.assertIn(word,self.page)
        self.assertIn('fictional',self.page.lower())
        self.assertIn('not anyone’s actual schedule',self.entry['quick_start']['example'])
    def test_single_download_source_matches_inline_preview(self):
        sheet=living_well.worksheet_exports()[Path('downloads/living-well-weekly-reset.md')]
        self.assertEqual((ROOT/'downloads/living-well-weekly-reset.md').read_text(),sheet)
        self.assertIn('<pre>'+escape(sheet)+'</pre>',self.page)
        self.assertIn('<pre>'+escape(sheet)+'</pre>',self.outputs[Path('living-well/worksheets/index.html')])
        self.assertIn('id="weekly-reset-worksheet"',self.page)
    def test_no_new_collection_and_existing_anchors_remain(self):
        for item in ('<form','<textarea','<input','fetch(','localStorage','sessionStorage'):
            self.assertNotIn(item,self.entry['quick_start']['intro']+self.entry['quick_start']['example'])
        for n in range(1,8):self.assertIn('id="part-'+str(n)+'"',self.page)
        self.assertIn('href="/downloads/living-well-weekly-reset.md" download',self.page)
        self.assertIn('href="/living-well/weekly-reset/#part-7"',self.outputs[Path('living-well/guides/index.html')])
        self.assertEqual(self.entry['published'],'2026-10-08')
        self.assertEqual(self.entry['updated'],'2026-10-17')
        self.assertIn('2026-10-17',self.outputs[Path('sitemap.xml')])
if __name__=='__main__':unittest.main()
