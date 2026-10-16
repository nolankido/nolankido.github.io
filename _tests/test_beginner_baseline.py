"""The observation kit cannot turn changed mechanics or draft status into evidence."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / '_reports/poker-beginner-baseline'
spec = spec_from_file_location('beginner_baseline', FOLDER / 'check_kit.py')
kit = module_from_spec(spec)
spec.loader.exec_module(kit)


class BeginnerBaselineTests(unittest.TestCase):
    def setUp(self):
        self.data = kit.teaching.read(ROOT, kit.FOLDER / 'tasks.json')
        self.lessons = kit.teaching.read(ROOT, '_source/poker/course-lessons.json')['lessons']

    def test_committed_exhibits_are_checked_and_keys_are_separate(self):
        self.assertEqual(len(kit.check()), 64)
        prompts = (FOLDER / 'participant-tasks.md').read_text()
        key = (FOLDER / 'facilitator-key.md').read_text()
        for task in self.data['tasks']:
            self.assertIn('## ' + task['id'] + '\n', prompts)
            self.assertIn(task['prompt'], prompts)
            for point in task['points']:
                self.assertNotIn(point, prompts)
                self.assertIn(point, key)
        self.assertIn('20/80 = 25%', key)
        self.assertIn('queen-high loses', key)

    def test_mechanical_errors_and_false_approval_fail(self):
        mutations = [
            lambda d: d.update(status='approved'),
            lambda d: d['tasks'][0]['hero'].__setitem__(1, 'As'),
            lambda d: d['tasks'][0].__setitem__('expected_rank', [1, 14, 10, 8, 4]),
            lambda d: d['tasks'][1]['call'].__setitem__('additional', 8),
            lambda d: d['tasks'][1]['alternate_call'].__setitem__('additional', 12),
            lambda d: d['tasks'][3]['river'].__setitem__('price', '1/3'),
            lambda d: d['tasks'][4]['expected_comparisons'].__setitem__(0, 'weaker'),
            lambda d: d['tasks'][5].__setitem__('skill', 'S1'),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                changed = deepcopy(self.data)
                mutation(changed)
                with self.assertRaises(ValueError):
                    kit.validate(changed, self.lessons)

    def test_stale_exhibits_and_changed_instrument_have_distinct_revisions(self):
        original = kit.check()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = [*(kit.FOLDER / name for name in kit.FILES),
                     *(kit.teaching.FOLDER / name for name in
                       (*kit.teaching.INSTRUMENTS, 'scope.json', 'packet.md',
                        'reference-text.md', 'answer-key.md', 'review-form.md', 'mechanics.json')),
                     *map(Path, kit.teaching.INPUTS), Path('_source/poker/resources.json')]
            for relative in paths:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            self.assertEqual(kit.check(root), original)
            form = root / kit.FOLDER / 'session-form.md'
            form.write_text(form.read_text() + '\nA deliberate template revision.\n')
            self.assertNotEqual(kit.check(root), original)
            prompts = root / kit.FOLDER / 'participant-tasks.md'
            prompts.write_text(prompts.read_text() + '\nStale prose.\n')
            with self.assertRaisesRegex(ValueError, 'Stale exhibit'):
                kit.check(root)
            lesson = root / '_source/poker/first-decisions.html'
            lesson.write_text(lesson.read_text() + '\nChanged teaching.\n')
            with self.assertRaisesRegex(ValueError, 'Teaching material changed'):
                kit.check(root)


if __name__ == '__main__':
    unittest.main()
