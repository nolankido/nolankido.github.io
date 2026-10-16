"""Build an inspectable, snapshot-bound review packet. Standard library only.

No network, learner records, reviewer certification or production renderer imports.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from html.parser import HTMLParser
from itertools import combinations
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
FOLDER = Path('_reports/poker-teaching-review')
SLUGS = ('first-decisions', 'starting-hand-decisions', 'first-flop-decisions',
         'turn-and-river-decisions', 'ranges-for-beginners', 'betting-with-a-purpose')
INPUTS = ('_source/poker/beginner-course.json', '_source/poker/course-lessons.json',
          '_source/poker/final-hands.json', '_source/poker/free-poker-learning-path.html',
          '_source/poker/beginner-checkpoint.html', '_scripts/poker_course.py',
          '_scripts/poker_lessons.py', '_scripts/poker_final_hands.py',
          *('_source/poker/' + slug + '.html' for slug in SLUGS))
INSTRUMENTS = ('rubric.json', 'README.md', 'build_packet.py')
NAMES = ('high card', 'one pair', 'two pair', 'three of a kind', 'straight',
         'flush', 'full house', 'four of a kind', 'straight flush')


def read(root, path):
    return json.loads((root / path).read_text(encoding='utf-8'))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def digest(value):
    return sha256(value).hexdigest()


def tda(root):
    return next(e for e in read(root, '_source/poker/resources.json')['entries'] if e['id'] == 'tda-rules')


def capture(root, commit):
    if not re.fullmatch('[0-9a-f]{40}', commit):
        raise ValueError('Use a full material commit SHA')
    files = {}
    for path in INPUTS:
        current = (root / path).read_bytes()
        original = subprocess.check_output(['git', 'show', commit + ':' + path], cwd=root)
        if current != original:
            raise ValueError('Material differs from the named commit: ' + path)
        files[path] = digest(current)
    original = json.loads(subprocess.check_output(
        ['git', 'show', commit + ':_source/poker/resources.json'], cwd=root))
    if tda(root) != next(e for e in original['entries'] if e['id'] == 'tda-rules'):
        raise ValueError('The TDA record differs from the material commit')
    scope = {'version': 1, 'material_commit': commit,
             'prepared_utc': datetime.now(timezone.utc).date().isoformat(),
             'human_review': 'pending', 'source_files': files, 'tda_record': tda(root),
             'instrument_files': {name: digest((root / FOLDER / name).read_bytes()) for name in INSTRUMENTS}}
    scope['fingerprint'] = digest(encoded(scope))
    return scope


def validate_scope(root, scope):
    payload = {k: v for k, v in scope.items() if k != 'fingerprint'}
    if digest(encoded(payload)) != scope['fingerprint']:
        raise ValueError('Review-scope fingerprint does not match')
    if scope['human_review'] != 'pending':
        raise ValueError('This packet generator cannot certify a human review')
    if set(scope['source_files']) != set(INPUTS):
        raise ValueError('Review scope must cover all core teaching inputs')
    for path, expected in scope['source_files'].items():
        if digest((root / path).read_bytes()) != expected:
            raise ValueError('Teaching material changed; prepare a new review scope: ' + path)
    if scope['tda_record'] != tda(root):
        raise ValueError('Current TDA evidence changed; prepare a new review scope')
    if scope['instrument_files'] != {name: digest((root / FOLDER / name).read_bytes()) for name in INSTRUMENTS}:
        raise ValueError('Review instrument changed; prepare a new review scope')


def best(cards):
    if (not 5 <= len(cards) <= 7 or len(set(cards)) != len(cards)
            or any(not re.fullmatch('[2-9TJQKA][shdc]', c) for c in cards)):
        raise ValueError('Rank five to seven distinct standard cards')
    def five(hand):
        ranks = sorted(('23456789TJQKA'.index(c[0]) + 2 for c in hand), reverse=True)
        groups = sorted(((n, r) for r, n in Counter(ranks).items()), reverse=True)
        distinct = sorted(set(ranks))
        straight = (5 if distinct == [2, 3, 4, 5, 14] else
                    max(ranks) if len(distinct) == 5 and distinct[-1] - distinct[0] == 4 else 0)
        flush = len({c[1] for c in hand}) == 1
        if straight and flush: return (8, straight)
        if groups[0][0] == 4: return (7, groups[0][1], groups[1][1])
        if [n for n, _ in groups] == [3, 2]: return (6, groups[0][1], groups[1][1])
        if flush: return (5, *ranks)
        if straight: return (4, straight)
        if groups[0][0] == 3: return (3, groups[0][1], *sorted((r for n, r in groups if n == 1), reverse=True))
        if [n for n, _ in groups] == [2, 2, 1]: return (2, *sorted((r for n, r in groups if n == 2), reverse=True), groups[-1][1])
        if groups[0][0] == 2: return (1, groups[0][1], *sorted((r for n, r in groups if n == 1), reverse=True))
        return (0, *ranks)
    return max(five(hand) for hand in combinations(cards, 5))


def comparison(hero, board, candidate):
    if (len(candidate) != 2 or len(set(candidate)) != 2
            or any(not re.fullmatch('[2-9TJQKA][shdc]', c) for c in candidate)):
        raise ValueError('A candidate needs two distinct cards')
    if set(candidate) & set(hero + board):
        return 'impossible'
    theirs, ours = best(candidate + board), best(hero + board)
    return 'stronger' if theirs > ours else 'weaker' if theirs < ours else 'tied'


def audit(root):
    rows = []
    lessons = read(root, '_source/poker/course-lessons.json')['lessons']
    if tuple(x['slug'] for x in lessons) != SLUGS:
        raise ValueError('Review must cover the six canonical lessons in order')
    for i, lesson in enumerate(lessons, 1):
        for kind, code in [('worked', 'W'), ('attempt', 'A')]:
            case = lesson[kind]
            cards = [c for g in case.get('cards', []) for c in g['values']]
            if len(cards) != len(set(cards)) or any(not re.fullmatch('[2-9TJQKA][shdc]', c) for c in cards):
                raise ValueError('Invalid lesson cards')
            rank = best(cards) if len(cards) >= 5 else None
            row = {'task': f'L{i}-{code}', 'best_rank': rank,
                   'category': NAMES[rank[0]] if rank else 'preflop: no five-card hand'}
            if case.get('candidates'):
                row['candidate_comparisons'] = [comparison(cards[:2], cards[2:], c['values']) for c in case['candidates']]
            rows.append(row)
    for hand in read(root, '_source/poker/final-hands.json')['hands']:
        all_cards = hand['hero'] + hand['board'] + hand['opponent']
        if [len(hand[k]) for k in ['hero', 'board', 'opponent']] != [2, 5, 2] or len(set(all_cards)) != 9:
            raise ValueError('Duplicate final-hand cards')
        previous = [0] * 6
        for stop in hand['stops']:
            if stop['board_count'] != {'Preflop': 0, 'Flop': 3, 'Turn': 4, 'River': 5}[stop['street']]:
                raise ValueError('Board exposure conflicts with the street')
            paid = stop['paid']
            if len(paid) != 6 or any(type(n) is not int or not a <= n <= 100 for a, n in zip(previous, paid)):
                raise ValueError('Invalid cumulative ledger')
            previous = paid
            call = stop['wager'] - stop['street_paid']
            if not 0 <= stop['street_paid'] <= paid[hand['hero_seat']] or call < 0:
                raise ValueError('Invalid current-round call')
            board = hand['board'][:stop['board_count']]
            rank = best(hand['hero'] + board) if board else None
            row = {'task': hand['id'].upper() + '-' + stop['street'].lower(),
                   'pot': sum(paid), 'additional_call': call, 'hero_behind': 100 - paid[hand['hero_seat']],
                   'best_rank': rank, 'category': NAMES[rank[0]] if rank else 'preflop: no five-card hand'}
            if stop.get('candidates'):
                row['candidate_comparisons'] = [comparison(hand['hero'], board, c['values']) for c in stop['candidates']]
            if stop['street'] == 'River':
                after = paid.copy(); after[hand['hero_seat']] += call
                if after != hand['finish_paid']:
                    raise ValueError('River call does not reconcile with the ending ledger')
                row['pot_after_call'] = sum(after)
                row['break_even_share'] = str(Fraction(call, sum(after)))
            rows.append(row)
        hero, opponent = best(hand['hero'] + hand['board']), best(hand['opponent'] + hand['board'])
        if hero == opponent:
            raise ValueError('These scripted endings require a single winner')
        winner = hand['hero_seat'] if hero > opponent else hand['opponent_seat']
        if winner != hand['winner_seat']:
            raise ValueError('Showdown winner conflicts with available cards')
        paid = hand['finish_paid']
        stacks = [100 - n for n in paid]; stacks[winner] += sum(paid)
        if sum(stacks) != 600 or any(n < 0 for n in stacks):
            raise ValueError('Ending stacks do not preserve 600 counters')
        rows.append({'task': hand['id'].upper() + '-showdown', 'pot_awarded': sum(paid),
                     'hero_rank': hero, 'opponent_rank': opponent, 'winner_seat': winner,
                     'ending_stacks': stacks, 'hero_net': stacks[hand['hero_seat']] - 100})
    guided = read(root, '_source/poker/beginner-course.json')['hand']
    if len(set(guided['hero'] + guided['opponent'] + guided['board'])) != 9:
        raise ValueError('Duplicate guided-hand cards')
    for scene in guided['scenes']:
        if scene['pot'] + scene['hero_behind'] + scene['opponent_behind'] + 99 + 300 != 600:
            raise ValueError('Guided-hand scene does not conserve counters')
        board = guided['board'][:scene['board_count']]
        rank = best(guided['hero'] + board) if board else None
        row = {'task': 'G-' + scene['id'], 'pot': scene['pot'], 'best_rank': rank,
               'category': NAMES[rank[0]] if rank else 'preflop: no five-card hand'}
        if scene['id'] == 'showdown':
            opponent = best(guided['opponent'] + guided['board'])
            if rank <= opponent or sum(guided['contributions']) != scene['pot']:
                raise ValueError('Guided showdown does not match cards or contributions')
            stacks = [100 - n for n in guided['contributions']]
            stacks[guided['hero_seat']] += scene['pot']
            if sum(stacks) != 600 or any(n < 0 for n in stacks):
                raise ValueError('Guided ending does not conserve counters')
            row.update(opponent_rank=opponent, ending_stacks=stacks,
                       hero_net=stacks[guided['hero_seat']] - 100)
        rows.append(row)
    return {'status': 'mechanical cross-check only; human review pending', 'cases': rows,
            'limits': ['Prose numbers, legal-action wording and pedagogy require reviewer inspection.',
                       'Candidate comparisons treat holdings as separate alternatives, without frequencies.',
                       'No equity model, solver result, learner outcome or optimal-action grade is computed.']}


def link(scope, path):
    return 'https://github.com/nolankido/nolankido.github.io/blob/' + scope['material_commit'] + '/' + path


def repair_exhibit(root, scope, route):
    target = urlsplit(route)
    slug = target.path.removeprefix('/poker/').strip('/')
    if (target.scheme or target.netloc or target.query or slug not in SLUGS
            or not re.fullmatch('[a-z0-9-]+', target.fragment)):
        raise ValueError('Repair must reach a scoped lesson section')
    path = '_source/poker/' + slug + '.html'
    pattern = re.compile(r'\bid=[\"\x27]' + re.escape(target.fragment) + r'[\"\x27]')
    locations = [n for n, text in enumerate((root / path).read_text(encoding='utf-8').splitlines(), 1) if pattern.search(text)]
    if len(locations) != 1:
        raise ValueError('Repair needs one exact source destination: ' + route)
    return ('Snapshot repair: [' + slug + ' #' + target.fragment + ']('
            + link(scope, path) + '#L' + str(locations[0]) + '); '
            '[readable exhibit](reference-text.md#ref-' + slug + '-' + target.fragment
            + '). Live navigation: https://nolankido.com' + route)


def stamp(scope):
    return ['Material commit: `' + scope['material_commit'] + '`.',
            'Packet fingerprint: `' + scope['fingerprint'] + '`.',
            'Prepared ' + scope['prepared_utc'] + ' UTC. **Human review: pending.**', '']


def case_text(lines, case):
    for paragraph in case['setup']: lines.extend([paragraph, ''])
    for group in case.get('cards', []) + case.get('candidates', []):
        lines.append('- ' + group['label'] + ': ' + ', '.join(group['values']))
    if case.get('table'):
        table = case['table']
        lines += ['- Six seats in order: first seat, next seat, cutoff, button, small blind, big blind.',
                  '- Hero seat index (zero-based): ' + str(table['hero']) + '; paid this round: ' + str(table['paid']) + '; folded: ' + str(table['folded']) + '.']
    lines.append('')
    if case.get('prompt'): lines.extend([case['prompt'], ''])


class ReferenceText(HTMLParser):
    def __init__(self, source, slug):
        super().__init__(convert_charrefs=True)
        self.lines, self.parts, self.skip, self.slug = [], [], 0, slug
        self.feed(source); self.flush()

    def flush(self):
        value = ' '.join(''.join(self.parts).split())
        if value: self.lines.extend([value, ''])
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}: self.skip += 1
        if self.skip: return
        anchor = dict(attrs).get('id')
        if anchor:
            if not re.fullmatch('[a-z0-9-]+', anchor):
                raise ValueError('Reference anchor needs a stable safe ID')
            self.flush()
            self.lines.extend(['<a id="ref-' + self.slug + '-' + anchor + '"></a>', ''])
        if tag in {'p', 'li', 'h1', 'h2', 'h3', 'summary', 'tr', 'figcaption'}:
            self.flush()
            if tag.startswith('h') and tag[1:].isdigit():
                self.parts.append('#### ')
            if tag == 'li': self.parts.append('- ')
            if anchor: self.parts.append('[' + anchor + '] ')
        if tag in {'td', 'th'} and self.parts: self.parts.append(' / ')

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}: self.skip -= 1
        if not self.skip and tag in {'p', 'li', 'h1', 'h2', 'h3', 'summary', 'tr', 'figcaption'}: self.flush()

    def handle_data(self, value):
        if not self.skip: self.parts.append(value)


def documents(root, scope):
    validate_scope(root, scope)
    rubric = read(root, FOLDER / 'rubric.json')['skills']
    lessons = read(root, '_source/poker/course-lessons.json')['lessons']
    if len(rubric) != 6 or any(len(s['criteria']) != 3 for s in rubric):
        raise ValueError('Review requires six skills with three criteria each')
    course = read(root, '_source/poker/beginner-course.json')
    hands = read(root, '_source/poker/final-hands.json')['hands']
    packet = ['# Poker Foundations: independent teaching review', '', *stamp(scope),
              'Read README.md for the review protocol. Work through the prompts before opening answer-key.md. Use reference-text.md to inspect the complete source-article text. This is a reviewer packet with fictional examples, not a beginner outcome study.', '',
              'Card codes: T=ten, J=jack, Q=queen, K=king, A=ace; s=spades, h=hearts, d=diamonds, c=clubs. Candidates are separate alternatives.', '']
    key = ['# Current feedback and mechanical cross-check', '', *stamp(scope),
           'This key reproduces the current teaching feedback for inspection. It is not an independent human approval. Check the current prose against the recomputed card and ledger evidence below.', '']
    form = ['# Blank reviewer response', '', *stamp(scope),
            'Complete a copy outside this public repository. Name and contact details are optional for private coordination; publish only an approved summary.', '',
            '- Reviewer name or private identifier:', '- Relevant poker teaching/rules experience:',
            '- Conflicts or involvement in authoring this material:', '- Date and time spent:',
            '- Actual material commit and fingerprint inspected:', '- Sections not inspected:', '',
            'Use **unreviewed**, **accept**, **revise**, or **block** for each criterion. Record the exact task/anchor and your independent reason. An unreviewed row is incomplete. Acceptance requires all material mechanics issues and disagreements to be resolved, with the scope recorded. Do not average away a blocker.', '',
            '| Criterion | Status | Task/anchor and independent evidence | Issue ID |',
            '| --- | --- | --- | --- |']
    for i, (skill, lesson) in enumerate(zip(rubric, lessons), 1):
        if skill['id'] != f'S{i}' or skill['lesson'] != lesson['slug'] or not skill['tasks']:
            raise ValueError('Rubric does not match the course order')
        if [c[0] for c in skill['criteria']] != [f'S{i}.{n}' for n in range(1, 4)]:
            raise ValueError('Review criteria need stable unique IDs')
        packet += [f'## {skill["id"]}. {skill["title"]}', '',
                   'Full source: ' + link(scope, '_source/poker/' + lesson['slug'] + '.html'),
                   'Live lesson: https://nolankido.com/poker/' + lesson['slug'] + '/#course-first-pass-title', '',
                   '### Accuracy and misconception criteria', '']
        for cid, accept, misconception in skill['criteria']:
            packet += ['- **' + cid + '**: ' + accept, '  - Watch for: ' + misconception]
            form.append('| ' + cid + ' | unreviewed | | |')
        packet += ['', 'Reviewer probe: ' + skill['probe'],
                   'Cross-check tasks: ' + ', '.join(skill['tasks']) + '.',
                   'Reference IDs: ' + ', '.join(skill['sources']) + '.', '',
                   '### Current short explanation', '']
        for paragraph in lesson['teach']: packet.extend([paragraph, ''])
        for kind, code in [('worked', 'W'), ('attempt', 'A')]:
            task = f'L{i}-{code}'
            packet += ['### ' + task + ': ' + ('worked model' if code == 'W' else 'independent attempt'), '']
            case_text(packet, lesson[kind])
            key += ['## ' + task, '']
            for paragraph in lesson[kind]['answer']: key.extend([paragraph, ''])
            if kind == 'attempt': key += [repair_exhibit(root, scope, lesson[kind]['repair']), '']
        packet += ['Before approving: inspect the full source article, its first-pass sections, and every repair destination for this skill. Record any confusing terms, missing assumptions or feedback that would let the misconception survive.', '']
    for hand in hands:
        packet += ['## ' + hand['title'], '', 'Six players start with 100 counters each. Blinds 1/2; no antes, fees, all-ins, side pots or prize effects. Seats: first seat, next seat, cutoff, button, small blind, big blind.',
                   'Hero private cards: ' + ', '.join(hand['hero']) + '.', '']
        for stop in hand['stops']:
            task = hand['id'].upper() + '-' + stop['street'].lower()
            packet += ['### ' + task, '', stop['setup'],
                       'Board available now: ' + (', '.join(hand['board'][:stop['board_count']]) or 'none') + '.',
                       'Cumulative paid by seat: ' + str(stop['paid']) + '. Current-round hero payment: ' + str(stop['street_paid']) + '; current wager: ' + str(stop['wager']) + '.', '']
            for c in stop.get('candidates', []): packet.append('- ' + c['label'] + ': ' + ', '.join(c['values']))
            packet += ['', stop['prompt'], '']
            for url, label in stop['repairs']:
                packet += [label + '. ' + repair_exhibit(root, scope, url), '']
            key += ['## ' + task, '']
            for paragraph in stop['answer']: key.extend([paragraph, ''])
        key += ['## ' + hand['id'].upper() + '-showdown', '', 'Opponent: ' + ', '.join(hand['opponent']) + '.', '']
        for paragraph in hand['ending']: key.extend([paragraph, ''])
    packet += ['## Guided hand: inspect the recognition choices and feedback', '',
               'Hero: ' + ', '.join(course['hand']['hero']) + '. Read each scene before the key; later cards and the opponent are revealed only where the scene does so.', '']
    for scene in course['hand']['scenes']:
        task = 'G-' + scene['id']
        packet += ['### ' + task, '', scene['action'], scene['question'], '']
        packet.extend('- **' + chr(65 + i) + '.** ' + label for i, (label, _) in enumerate(scene['choices']))
        packet += ['', repair_exhibit(root, scope, scene['repair']), '']
        key += ['## ' + task, '', 'Current selected answer: ' + chr(65 + scene['correct']) + '.', scene['solution'],
                '', *['- **' + chr(65 + i) + ':** ' + reason for i, (_, reason) in enumerate(scene['choices'])], '']
        if scene.get('extra'): key += [scene['extra'], '']
        key += [repair_exhibit(root, scope, scene['repair']), '']
    evidence = audit(root)
    tasks = {r['task'] for r in evidence['cases']}
    if any(task not in tasks for s in rubric for task in s['tasks']):
        raise ValueError('Rubric links to an absent task')
    key += ['## Independent recomputation from structured fields', '',
            'Rank tuples are category followed by category-relevant ranks or kickers. Categories run 0 high card through 8 straight flush. Numeric ranks run 2 through 14 (ace). Preflop cards have no five-card rank.', '',
            '| Task | Recomputed facts |', '| --- | --- |']
    for row in evidence['cases']:
        key.append('| ' + row['task'] + ' | ' + json.dumps({k: v for k, v in row.items() if k != 'task'}, ensure_ascii=False) + ' |')
    key += ['', 'M1: Let P be the pot including the opposing bet and C the additional final call. With no fees, side pots, future betting or prize effects, a modeled expected pot share e has incremental call expectation e(P+C)-C versus folding. Setting this to zero gives e=C/(P+C). This identity supplies a price; it does not estimate e or compare raising.', '',
            'M2: A physically legal candidate identifies a possible holding. Probability needs a model or evidence about frequencies. One compatible reveal cannot uniquely identify those frequencies. These are editorial reasoning checks, not measured player tendencies.', '', *evidence['limits'], '']
    form += ['', '## Issue and disagreement log', '',
             'Copy this block for each issue. Material severity covers wrong cards, action, payment, winner, price or unsupported strategic/learning claims. Teaching severity covers an unclear prompt, missing misconception repair or confusing sequence. Editorial severity covers wording/presentation with no change in meaning.', '',
             '- Issue ID / criterion / task or exact anchor:', '- Severity (material / teaching / editorial):',
             '- Exact current claim:', '- Independent calculation or source and applicable rule:',
             '- Proposed correction and why:', '- Author response:', '- Reviewer disagreement and resolution:',
             '- Corrected commit, retest evidence and reviewer recheck:', '- Status (open / resolved / deferred with reason):', '',
             '## Final disposition', '', '- All 18 criteria inspected? (yes/no; list omissions):',
             '- All six full lesson articles, 12 short examples, eight final-hand stops and six guided scenes inspected? (yes/no; list omissions):',
             '- Open material issues:', '- Open teaching issues and proposed treatment:',
             '- Unresolved disagreements:', '- Accept this exact material scope / request revisions / incomplete:',
             '- Reviewer confirmation and date:',
             '- Approved public summary, if any:', '',
             'A completed form is editorial evidence for this snapshot. It does not certify learner mastery, profitable play, observed learning gains or readiness for a paid course.', '']
    record = scope['tda_record']; version = record['source_version']
    reference = ['# Full source-article text for the reviewer', '', *stamp(scope),
                 'Plain text extraction from the six source articles. The short-lesson additions and final hands are in packet.md. Follow source links when table layout or a diagram matters; this text extraction is not an accessibility audit.', '']
    published = datetime.strptime(version['published_on'], '%Y-%m-%d').date()
    reviewed = datetime.strptime(record['reviewed_on'], '%Y-%m-%d').date()
    label = lambda d: f'{d.strftime("%B")} {d.day}, {d.year}'
    tokens = {'poker_tda_long_label': f'{version["edition"]} Rules, Version {version["version"]}, {label(published)}',
              'poker_tda_reviewed_label': label(reviewed), 'poker_tda_label': f'Poker TDA: {version["edition"]} rules, version {version["version"]}'}
    for slug in SLUGS:
        path = '_source/poker/' + slug + '.html'
        source = (root / path).read_text(encoding='utf-8')
        for token, value in tokens.items(): source = source.replace('${' + token + '}', value)
        if '${' in source: raise ValueError('Unresolved source text in reviewer reference')
        reference += ['## ' + slug, '', link(scope, path), '', *ReferenceText(source, slug).lines]
    return {'packet.md': '\n'.join(packet), 'answer-key.md': '\n'.join(key),
            'review-form.md': '\n'.join(form), 'reference-text.md': '\n'.join(reference),
            'mechanics.json': encoded({'scope_fingerprint': scope['fingerprint'], **evidence}).decode()}


def check(root):
    scope = read(root, FOLDER / 'scope.json')
    for name, expected in documents(root, scope).items():
        if (root / FOLDER / name).read_text(encoding='utf-8') != expected:
            raise ValueError('Review document is stale: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--material-commit')
    args = parser.parse_args()
    if args.write:
        if not args.material_commit: parser.error('--write needs --material-commit')
        scope = capture(ROOT, args.material_commit)
        outputs = documents(ROOT, scope)
        for name, value in outputs.items(): (ROOT / FOLDER / name).write_text(value, encoding='utf-8')
        (ROOT / FOLDER / 'scope.json').write_bytes(encoded(scope))
    else:
        if args.material_commit: parser.error('--material-commit is only used with --write')
        check(ROOT)
    print('PASS: six-skill packet, 18 review criteria and 28 mechanical evidence rows; human review pending.')


if __name__ == '__main__': main()
