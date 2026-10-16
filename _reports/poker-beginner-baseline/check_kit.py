"""Check a blank observation kit, never certify human review or read learner data."""
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = Path('_reports/poker-beginner-baseline')
FILES = ('README.md', 'protocol.md', 'session-form.md', 'summary-form.md', 'probe-review-form.md',
         'tasks.json', 'check_kit.py', 'participant-tasks.md', 'facilitator-key.md')
spec = spec_from_file_location('baseline_teaching_oracle',
                              ROOT / '_reports/poker-teaching-review/build_packet.py')
teaching = module_from_spec(spec)
spec.loader.exec_module(teaching)
RANKS = dict(zip('23456789TJQKA',
                ('two', 'three', 'four', 'five', 'six', 'seven', 'eight',
                 'nine', 'ten', 'jack', 'queen', 'king', 'ace')))
SUITS = dict(zip('cdhs', ('clubs', 'diamonds', 'hearts', 'spades')))


def cards(values):
    return ', '.join(RANKS[c[0]] + ' of ' + SUITS[c[1]] + ' (' + c + ')' for c in values)


def validate(data, lessons):
    if data.get('version') != 1 or data.get('status') != 'draft-human-review-pending':
        raise ValueError('The kit cannot certify human approval or observations')
    tasks = data['tasks']
    if [t['id'] for t in tasks] != ['T' + str(i) for i in range(1, 7)]:
        raise ValueError('Exactly six ordered follow-up tasks are required')
    for i, (task, lesson) in enumerate(zip(tasks, lessons), 1):
        if task['lesson'] != lesson['slug'] or task['skill'] != 'S' + str(i):
            raise ValueError('Lesson/skill allocation changed')
        if len(task['hero']) != 2 or len(task['board']) not in (0, 3, 5):
            raise ValueError('Invalid hold\'em task state')
        available = task['hero'] + task['board']
        if len(set(available)) != len(available):
            raise ValueError('Duplicate physical card')
        for c in available:
            if len(c) != 2 or c[0] not in RANKS or c[1] not in SUITS:
                raise ValueError('Invalid physical card')
        if len(available) >= 5:
            if list(teaching.best(available)) != task['expected_rank']:
                raise ValueError('Incorrect best-five rank: ' + task['id'])
        elif 'expected_rank' in task:
            raise ValueError('A preflop hand has no five-card rank')
        if (not task['setup'].strip() or not task['prompt'].strip()
                or len(task['points']) != 3 or any(not p.strip() for p in task['points'])):
            raise ValueError('Task needs a setup, prompt and three scoring points')
        has_candidates = 'candidates' in task
        has_comparisons = 'expected_comparisons' in task
        if has_candidates != has_comparisons:
            raise ValueError('Candidate cards and comparison expectations must appear together')
        if task['skill'] in ('S5', 'S6') and not has_candidates:
            raise ValueError('Range and bet-purpose probes require candidate cards')
        if has_candidates:
            if (not isinstance(task['candidates'], list) or not task['candidates']
                    or not isinstance(task['expected_comparisons'], list)
                    or len(task['candidates']) != len(task['expected_comparisons'])):
                raise ValueError('Candidate cards and comparisons need matching nonzero lengths')
            comparisons = [teaching.comparison(task['hero'], task['board'], c)
                           for c in task['candidates']]
            if comparisons != task['expected_comparisons']:
                raise ValueError('Incorrect candidate comparison: ' + task['id'])
        for name in ('call', 'alternate_call'):
            if name not in task:
                continue
            call = task[name]
            if (set(call) != {'wager', 'paid_this_round', 'additional'}
                    or any(type(v) is not int or v < 0 for v in call.values())
                    or call['wager'] - call['paid_this_round'] != call['additional']):
                raise ValueError('Incorrect additional payment: ' + task['id'])
        if 'river' in task:
            river = task['river']
            for name in ('pot_before_bet', 'bet', 'current_pot', 'final_pot'):
                if type(river[name]) is not int or river[name] <= 0:
                    raise ValueError('River pots must be positive counters')
            if (river['pot_before_bet'] + river['bet'] != river['current_pot']
                    or river['current_pot'] + task['call']['additional'] != river['final_pot']
                    or river['bet'] != task['call']['wager']
                    or Fraction(task['call']['additional'], river['final_pot']) != Fraction(river['price'])):
                raise ValueError('Incorrect river ledger or price: ' + task['id'])
    return tasks


def exhibits(tasks):
    prompts = ['# Follow-up problems: participant view', '',
               'Draft pending qualified human review. Show only the assigned section.',
               'All situations are fictional. Counters have no monetary value. No wager is required.',
               'Explain your reasoning; it is fine to say what you do not know.', '']
    key = ['# Follow-up scoring guide: facilitator only', '',
           '**Draft. Qualified human review is pending. No learner results are supplied.**', '',
           'Keep this key closed until the first explanation has been recorded.',
           'For each point record supported / error / not demonstrated, with the actual reason.',
           'A bare correct number with an incorrect reason does not support the reasoning point.',
           'These are proposed observation points, not a validated scale or a mastery score.', '',
           'Cards, ranks, candidate comparisons and numeric call fields below are mechanically',
           'cross-checked. Prose, pedagogy, task equivalence and human explanations require review.', '']
    for task in tasks:
        prompts += ['## ' + task['id'], '', task['setup'], '',
                    'Your private cards: ' + cards(task['hero']) + '.', '',
                    'Shared board: ' + (cards(task['board']) if task['board'] else 'not dealt yet') + '.', '']
        for i, candidate in enumerate(task.get('candidates', []), 1):
            prompts += ['Candidate ' + str(i) + ': ' + cards(candidate) + '.', '']
        prompts += [task['prompt'], '']
        if 'alternate_call' in task:
            alternate = task['alternate_call']
            prompts += ['In a different hand with the same private cards, seats and blinds, '
                        + 'cutoff raises to ' + str(alternate['wager']) + ', button calls '
                        + str(alternate['wager']) + ' and small blind folds. '
                        + 'You have posted ' + str(alternate['paid_this_round'])
                        + ' as the big blind. What would you add to call then, and why?', '']
        key += ['## ' + task['id'] + ' / ' + task['skill'] + ' / ' + task['lesson'], '']
        key += [str(i) + '. ' + p for i, p in enumerate(task['points'], 1)] + ['']
        if 'expected_rank' in task:
            rank = task['expected_rank']
            key += ['Checked rank: ' + teaching.NAMES[rank[0]] + '; numeric tie-break vector '
                    + str(rank[1:]) + ' (2 to 14, ace high).', '']
        if 'expected_comparisons' in task:
            key += ['Checked candidate order: ' + ', '.join(task['expected_comparisons']) + '.', '']
        for name in ('call', 'alternate_call'):
            if name in task:
                call = task[name]
                key += ['Checked ' + name + ': ' + str(call['wager']) + ' minus '
                        + str(call['paid_this_round']) + ' = ' + str(call['additional']) + ' additional.', '']
        if 'river' in task:
            river = task['river']
            key += ['Checked river: ' + str(river['pot_before_bet']) + ' + ' + str(river['bet'])
                    + ' = ' + str(river['current_pot']) + ' before calling; '
                    + str(river['final_pot']) + ' after calling; price '
                    + river['price'] + ' = ' + format(float(Fraction(river['price'])) * 100, 'g') + '%.', '']
    return {'participant-tasks.md': '\n'.join(prompts), 'facilitator-key.md': '\n'.join(key)}


def check(root=ROOT, write=False):
    teaching.check(root)
    data = teaching.read(root, FOLDER / 'tasks.json')
    lessons = teaching.read(root, '_source/poker/course-lessons.json')['lessons']
    tasks = validate(data, lessons)
    for name, expected in exhibits(tasks).items():
        path = root / FOLDER / name
        if write:
            path.write_text(expected, encoding='utf-8')
        elif not path.exists() or path.read_text(encoding='utf-8') != expected:
            raise ValueError('Stale exhibit: ' + str(path.relative_to(root)))
    scope = teaching.read(root, teaching.FOLDER / 'scope.json')
    revisions = {'teaching_fingerprint': scope['fingerprint'],
                 'kit_files': {name: sha256((root / FOLDER / name).read_bytes()).hexdigest()
                               for name in FILES}}
    return sha256(teaching.encoded(revisions)).hexdigest()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate draft prompt/key exhibits only')
    args = parser.parse_args()
    fingerprint = check(write=args.write)
    print('PREPARATION CHECK OK. Human reviews and learner observations remain pending.')
    print('Kit fingerprint: ' + fingerprint)
