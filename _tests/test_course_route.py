"""A visible course sequence, optional repair tools and the exact predecessor."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import re
import unittest
import html5lib
from test_site import ROOT, build
import poker_course
import course_route_history as history


class CourseRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=build.build_outputs()
        cls.html=cls.outputs[build.output_path(poker_course.ROUTE)]
        cls.doc=html5lib.parse(cls.html,namespaceHTMLElements=False)
        cls.baseline=json.loads((ROOT/'_tests/course-route-baseline.json').read_text())

    def test_exact_published_predecessor_and_inventory_survive_the_reviewed_change(self):
        b=self.baseline
        self.assertEqual((b['commit'],len(b['pages']),len(b['outputs']),len(b['files'])),('2e9f369d57be882cc9ffbaf983056af3f4d1e07e',193,221,480))
        self.assertEqual(history.pages(build.public_pages()),b['pages'])
        restored=history.outputs(self.outputs)
        self.assertEqual(set(map(str,restored)),set(b['outputs']))
        for path,text in restored.items():
            self.assertEqual(sha256(text.encode()).hexdigest(),b['outputs'][str(path)],str(path))
        for path,digest in {**b['files'],**b['extras']}.items():
            self.assertEqual(sha256(history.before(path,(ROOT/path).read_bytes())).hexdigest(),digest,path)
        actual={p.relative_to(ROOT).as_posix() for d in ['_source','_scripts','assets','downloads'] for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        self.assertEqual(actual,set(b['files']))
        self.assertEqual(history.change()['new_files'],{})
        self.assertEqual(history.change()['new_pages'],{})
        self.assertEqual(history.change()['new_outputs'],{})

    def test_entrance_and_map_expose_the_course_before_all_supporting_tools(self):
        ids=[e.get('id') for e in self.doc.iter() if e.get('id')]
        ordered=['beginner-practice','course-finish','practice-tools','card-basics','first-hand-practice','betting-rehearsal','how-to-use']
        self.assertEqual(sorted(ordered,key=ids.index),ordered)
        for ident in self.baseline['course_anchors']:
            self.assertEqual(ids.count(ident),1,ident)
        self.assertEqual(set(ids)-set(self.baseline['course_anchors']),{'practice-tools'})
        intro=next(e for e in self.doc.iter('div') if e.get('class')=='link-row')
        primary=next(a for a in intro.iter('a') if a.get('class')=='button')
        self.assertEqual(primary.get('href'),'/poker/first-decisions/')
        self.assertIn('#card-basics',[a.get('href') for a in intro.iter('a')])
        course=next(e for e in self.doc.iter('section') if e.get('id')=='beginner-practice')
        self.assertEqual([a.get('href') for h in course.iter('h3') for a in h.iter('a')],['/poker/'+slug+'/' for slug,_ in poker_course.LESSONS])
        self.assertLess(len(re.sub('<[^>]+>',' ',self.html.split('id="beginner-practice"')[0]).split()),1000)

    def test_optional_menu_and_card_basics_provide_real_continuations(self):
        menu=next(e for e in self.doc.iter('section') if e.get('class')=='course-tool-menu')
        choices=next(menu.iter('ul'))
        self.assertEqual([next(li.iter('a')).get('href') for li in choices],['#card-basics','#first-hand-practice','#betting-rehearsal'])
        for li in choices:
            self.assertGreater(len(' '.join(li.itertext()).split()),20)
        ready=next(e for e in self.doc.iter('p') if e.get('class')=='hand-basics-ready')
        self.assertEqual(next(ready.iter('a')).get('href'),'/poker/first-decisions/')
        self.assertIn('optional',' '.join(ready.itertext()))
        for name in ['hand-foundations-next','course-practice-return']:
            return_link=next(e for e in self.doc.iter('p') if e.get('class')==name)
            self.assertIn('#beginner-practice',[a.get('href') for a in return_link.iter('a')])

    def test_exercise_data_scripts_downloads_and_full_lessons_are_unchanged(self):
        b=self.baseline
        for path,digest in b['files'].items():
            if path.endswith('.js') or path.startswith('downloads/') or path in ['_source/poker/'+slug+'.html' for slug,_ in poker_course.LESSONS] or path in ['_source/poker/beginner-course.json','_source/poker/course-lessons.json','_source/poker/hand-lab.json','_source/poker/round-practice.json','_source/poker/final-hands.json']:
                self.assertEqual(sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
        self.assertEqual(self.html.count('data-lab-case'),10)
        self.assertEqual(self.html.count('data-course-scene '),6)
        self.assertNotIn('<form',self.html)
        changed=self.html+'Unreviewed change'
        self.assertEqual(history.before('poker/free-poker-learning-path/index.html',changed),changed)
        raw=(ROOT/'_scripts/poker_hand_lab.py').read_bytes()+b'\n# Unreviewed change'
        self.assertEqual(history.before('_scripts/poker_hand_lab.py',raw),raw)
        pages=deepcopy(build.public_pages());next(p for p in pages if p['path']==poker_course.ROUTE)['description']+='Unreviewed claim'
        self.assertNotEqual(history.pages(pages),b['pages'])


if __name__=='__main__':unittest.main()
