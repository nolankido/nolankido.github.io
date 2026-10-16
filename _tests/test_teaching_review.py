"""Review exhibits stay tied to actual teaching, without inventing human signoff."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / '_reports/poker-teaching-review'
spec = spec_from_file_location('teaching_review_packet', FOLDER / 'build_packet.py')
packet = module_from_spec(spec)
spec.loader.exec_module(packet)


class TeachingReviewTests(unittest.TestCase):
    def copy_material(self, root):
        for relative in [*packet.INPUTS, '_source/poker/resources.json',
                         *(str(packet.FOLDER / name) for name in packet.INSTRUMENTS),
                         str(packet.FOLDER / 'scope.json')]:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / relative).read_bytes())

    def test_committed_packet_covers_all_tasks_and_keeps_review_pending(self):
        packet.check(ROOT)
        scope = packet.read(ROOT, packet.FOLDER / 'scope.json')
        self.assertEqual(scope['material_commit'], '74f438934beca0ab2563af0dfe279923d588f0f1')
        self.assertEqual(len(scope['source_files']), 14)
        self.assertEqual(scope['human_review'], 'pending')
        rubric = packet.read(ROOT, packet.FOLDER / 'rubric.json')['skills']
        self.assertEqual([s['id'] for s in rubric], ['S1', 'S2', 'S3', 'S4', 'S5', 'S6'])
        self.assertEqual(len({c[0] for s in rubric for c in s['criteria']}), 18)
        form = (FOLDER / 'review-form.md').read_text()
        self.assertEqual(form.count('| unreviewed |'), 18)
        exhibits = (FOLDER / 'packet.md').read_text()
        for task in [f'L{i}-A' for i in range(1, 7)] + [h + '-' + s for h in ['A', 'B'] for s in ['preflop', 'flop', 'turn', 'river']]:
            self.assertIn('### ' + task, exhibits)
        self.assertNotIn('Current selected answer:', exhibits)

    def test_independent_ranker_handles_categories_ties_and_physical_limits(self):
        fixtures = [
            ('As Kd Qc Jh 9s', (0,14,13,12,11,9)),
            ('As Ad Kc Qh 9s', (1,14,13,12,9)),
            ('As Ad Kc Kh 9s', (2,14,13,9)),
            ('As Ad Ac Kh 9s', (3,14,13,9)),
            ('As 2d 3c 4h 5s', (4,5)),
            ('As Js 9s 5s 2s', (5,14,11,9,5,2)),
            ('As Ad Ac Kh Ks', (6,14,13)),
            ('As Ad Ac Ah Ks', (7,14,13)),
            ('9s Ts Js Qs Ks', (8,13))]
        for cards, expected in fixtures:
            self.assertEqual(packet.best(cards.split()), expected)
        board = 'As Ks Qs Js Ts'.split()
        self.assertEqual(packet.best(board + ['2c','3d']), packet.best(board + ['4h','5d']))
        self.assertGreater(packet.best('As Js 9s 5s 2s'.split()), packet.best('Ah Th 9h 5h 2h'.split()))
        for cards in [['As']*5, ['Xs','Kd','Qc','Jh','9s'], ['As','Kd']]:
            with self.assertRaises(ValueError): packet.best(cards)
        with self.assertRaises(ValueError):
            packet.comparison(['Ah','Th'], ['Tc','7h','2h','4c','9s'], ['Ah','Xs'])

    def test_evidence_exposes_exact_prices_candidates_and_all_ending_stacks(self):
        rows = {r['task']: r for r in packet.audit(ROOT)['cases']}
        self.assertEqual(len(rows), 28)
        self.assertEqual((rows['A-river']['pot'], rows['A-river']['additional_call'], rows['A-river']['pot_after_call'], rows['A-river']['break_even_share']), (28,7,35,'1/5'))
        self.assertEqual((rows['B-river']['pot'], rows['B-river']['additional_call'], rows['B-river']['pot_after_call'], rows['B-river']['break_even_share']), (42,14,56,'1/4'))
        self.assertEqual(rows['A-showdown']['ending_stacks'], [100,100,100,83,99,118])
        self.assertEqual(rows['B-showdown']['ending_stacks'], [100,100,73,100,129,98])
        self.assertEqual(rows['A-river']['candidate_comparisons'], ['impossible','weaker','stronger'])
        self.assertEqual(rows['B-river']['candidate_comparisons'], ['impossible','stronger','weaker'])
        self.assertEqual(rows['L6-A']['best_rank'], (1,9,11,8,7))
        self.assertEqual(rows['G-showdown']['ending_stacks'], [100,100,100,129,99,72])

    def test_all_feedback_and_repairs_have_snapshot_bound_exhibits(self):
        key = (FOLDER / 'answer-key.md').read_text()
        prompts = (FOLDER / 'packet.md').read_text()
        reference = (FOLDER / 'reference-text.md').read_text()
        scope = packet.read(ROOT, packet.FOLDER / 'scope.json')
        guided = packet.read(ROOT, '_source/poker/beginner-course.json')['hand']['scenes']
        def section(text, task, level):
            match = re.search(r'(?ms)^' + '#' * level + ' ' + re.escape(task)
                              + r'\n(.*?)(?=^#{1,' + str(level) + r'} |\Z)', text)
            self.assertIsNotNone(match, task)
            return match[1]
        groups = [(lesson['attempt']['repair'], section(key, f'L{i}-A', 2))
                  for i, lesson in enumerate(packet.read(ROOT, '_source/poker/course-lessons.json')['lessons'], 1)]
        groups += [(url, section(prompts, h['id'].upper() + '-' + s['street'].lower(), 3))
                   for h in packet.read(ROOT, '_source/poker/final-hands.json')['hands']
                   for s in h['stops'] for url, _ in s['repairs']]
        for scene in guided:
            feedback = section(key, 'G-' + scene['id'], 2)
            if scene.get('extra'): self.assertIn(scene['extra'], feedback)
            groups += [(scene['repair'], feedback), (scene['repair'], section(prompts, 'G-' + scene['id'], 3))]
        for route, text in groups:
            target = urlsplit(route)
            slug = target.path.strip('/').split('/')[-1]
            pinned = 'https://github.com/nolankido/nolankido.github.io/blob/' + scope['material_commit'] + '/_source/poker/' + slug + '.html#L'
            self.assertIn(pinned, text)
            self.assertIn('(reference-text.md#ref-' + slug + '-' + target.fragment + ')', text)
            self.assertIn('<a id="ref-' + slug + '-' + target.fragment + '"></a>', reference)
        with self.assertRaises(ValueError):
            packet.repair_exhibit(ROOT, scope, '/poker/first-decisions/#nonexistent')

    def test_invalid_cards_winners_and_ledgers_cannot_receive_a_clean_report(self):
        original = packet.read(ROOT, '_source/poker/final-hands.json')
        changes = []
        bad = deepcopy(original); bad['hands'][0]['winner_seat'] = 3; changes.append(bad)
        bad = deepcopy(original); bad['hands'][0]['opponent'][0] = 'Ah'; changes.append(bad)
        bad = deepcopy(original); bad['hands'][1]['finish_paid'][4] = 26; changes.append(bad)
        bad = deepcopy(original); bad['hands'][0]['stops'][2]['paid'][3] = 5; changes.append(bad)
        with TemporaryDirectory() as tmp:
            root = Path(tmp); self.copy_material(root)
            for bad in changes:
                (root / '_source/poker/final-hands.json').write_text(json.dumps(bad))
                with self.assertRaises(ValueError): packet.audit(root)

    def test_scope_rejects_changed_teaching_or_signoff_but_ignores_unrelated_resources(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp); self.copy_material(root)
            scope = packet.read(root, packet.FOLDER / 'scope.json')
            resources = packet.read(root, '_source/poker/resources.json')
            resources['entries'][1]['notes'] += ' Another resource review.'
            (root / '_source/poker/resources.json').write_text(json.dumps(resources))
            packet.validate_scope(root, scope)
            lesson = root / '_source/poker/first-decisions.html'
            lesson.write_text(lesson.read_text() + ' Changed explanation.')
            with self.assertRaisesRegex(ValueError, 'Teaching material changed'):
                packet.validate_scope(root, scope)
            forged = deepcopy(scope); forged['human_review'] = 'approved'
            forged['fingerprint'] = packet.digest(packet.encoded({k:v for k,v in forged.items() if k!='fingerprint'}))
            with self.assertRaisesRegex(ValueError, 'cannot certify'):
                packet.validate_scope(ROOT, forged)


if __name__ == '__main__': unittest.main()
