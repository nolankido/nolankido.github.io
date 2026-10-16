"""Native short lessons: teach, model, explain a changed case, continue."""
from html import escape
from datetime import date
import json
import re

DATA = '_source/poker/course-lessons.json'
SEATS = ('First seat', 'Next seat', 'Cutoff', 'Button', 'Small blind', 'Big blind')


def validate_table(table):
    """These maps describe a six-player initial preflop turn, without all-ins."""
    if not isinstance(table, dict) or set(table) != {'hero', 'paid', 'folded'}:
        raise ValueError('A position map needs a current seat, six payments and folds')
    hero, paid, folded = table['hero'], table['paid'], table['folded']
    if type(hero) is not int or not 0 <= hero < 5 or not isinstance(paid, list) or len(paid) != 6 or any(type(n) is not int or not 0 <= n < 100 for n in paid):
        raise ValueError('Position maps use six seats and payments below the 100-counter starting stack')
    if not isinstance(folded, list) or any(type(n) is not int or not 0 <= n < hero for n in folded) or len(set(folded)) != len(folded):
        raise ValueError('Only distinct earlier seats can have folded before this initial turn')
    if paid[4] != 1 or paid[5] != 2 or any(paid[i] != 0 for i in range(hero, 4)) or any(paid[i] != 0 for i in folded):
        raise ValueError('Seats still to act retain only their 1/2 blinds')
    wager = max(paid)
    if any(paid[i] != wager for i in range(hero) if i not in folded) or wager == 3:
        raise ValueError('Earlier live seats must have matched a legal opening wager')


def load(root, slugs):
    data = json.loads((root / DATA).read_text(encoding='utf-8'))
    if data.get('version') != 1 or [r['slug'] for r in data['lessons']] != list(slugs):
        raise ValueError('Short lessons must match the six canonical course lessons')
    for lesson in data['lessons']:
        for key in ['idea', 'recall']:
            if not isinstance(lesson.get(key), str) or not lesson[key].strip():
                raise ValueError('Short lessons need an idea and a recall task')
        for paragraphs in [lesson['teach'], lesson['worked']['setup'], lesson['worked']['answer'], lesson['attempt']['setup'], lesson['attempt']['answer']]:
            if not paragraphs or any(not isinstance(p, str) or not p.strip() for p in paragraphs):
                raise ValueError('Short lessons need teaching, examples and explained attempts')
        if not lesson['attempt']['prompt'].strip():
            raise ValueError('Each attempt needs a learner explanation prompt')
        for case in [lesson['worked'], lesson['attempt']]:
            if lesson['slug'] == 'starting-hand-decisions' and 'table' not in case:
                raise ValueError('Both position examples need their six-seat map')
            if 'table' in case:
                if lesson['slug'] != 'starting-hand-decisions':
                    raise ValueError('The six-seat preflop maps belong to the position lesson')
                validate_table(case['table'])
            known = []
            for kind in ['cards', 'candidates']:
                for group in case.get(kind, []):
                    values = group['values']
                    if not group['label'].strip() or not 1 <= len(values) <= 5 or len(set(values)) != len(values) or any(not re.fullmatch(r'[2-9TJQKA][shdc]', c) for c in values):
                        raise ValueError('Lesson cards need distinct standard cards and a label')
                    if kind == 'cards':
                        known.extend(values)
            if len(set(known)) != len(known):
                raise ValueError('Private and shared cards must not overlap')
        route, anchor = lesson['attempt']['repair'].split('#')
        if route != '/poker/' + lesson['slug'] + '/' or 'id="' + anchor + '"' not in (root / '_source/poker' / (lesson['slug'] + '.html')).read_text():
            raise ValueError('Each explanation must repair to its own published lesson')
    return data['lessons']


def paragraphs(values):
    return ''.join('<p>' + escape(value) + '</p>' for value in values)


def position_map(table):
    if table is None:
        return ''
    seats = []
    for i, name in enumerate(SEATS):
        state = 'Folded' if i in table['folded'] else 'You: your turn' if i == table['hero'] else 'Already acted' if i < table['hero'] else 'Not acted yet'
        classes = 'course-position-seat' + (' is-you' if i == table['hero'] else '') + (' is-folded' if i in table['folded'] else '')
        button = '<span class="course-position-button">Dealer button</span>' if i == 3 else ''
        seats.append('<li class="' + classes + '"><span class="course-position-number"><span class="visually-hidden">Seat </span>' + str(i + 1) + '</span><strong>' + name + '</strong>' + button + '<span>' + state + '</span><span>Paid ' + str(table['paid'][i]) + '</span></li>')
    return ('<figure class="course-position-map"><figcaption><strong>Find your seat before reading your cards.</strong> Six seats, numbered clockwise for this hand. Seat 1 starts preflop; the button moves for the next hand. Payments are counters on this round.</figcaption>'
            '<div class="course-position-layout"><span class="course-position-felt" aria-hidden="true"></span><ol role="list" aria-label="Six seats in clockwise initial preflop order">' + ''.join(seats) + '</ol></div></figure>')


def position_orders(table):
    if table is None:
        return ''
    def queue(indices, label):
        rows = ''.join('<li>' + SEATS[i] + (' (you)' if i == table['hero'] else '') + '</li>' for i in indices)
        return '<div><p><strong>' + label + '</strong></p><ol>' + rows + '</ol></div>'
    pending = [i for i in range(table['hero'] + 1, 6) if i not in table['folded']]
    flop = [i for i in [4, 5, 0, 1, 2, 3] if i not in table['folded']]
    return ('<div class="course-position-orders">' + queue(pending, 'Next initial turns before the flop') + queue(flop, 'First turns on the flop, if every live seat continues') + '</div>'
            '<p class="course-position-note">Skip folded seats. These are initial turns, not a complete betting round: a later bet or raise can give an earlier player another decision. The maps describe six players, not the special two-player blind rules.</p>')


def case_display(case, card_renderer):
    groups = case.get('cards', []) + case.get('candidates', [])
    cards = '<div class="course-lesson-cards">' + ''.join('<div><p class="course-state-label">' + escape(g['label']) + '</p>' + card_renderer(g['values']) + '</div>' for g in groups) + '</div>' if groups else ''
    return paragraphs(case['setup']) + position_map(case.get('table')) + cards


def render(lesson, card_renderer, next_route, next_label, optional, revision, updated='2026-10-15'):
    attempt = lesson['attempt']
    revised = date.fromisoformat(updated)
    stamp = f'{revised:%B} {revised.day}, {revised.year}'
    return ('<p class="course-lesson-intro">Work through this short lesson, then pause or continue. The full explanation and other practice are available below.</p>'
            '<h3 id="course-lesson-idea">1. Learn one idea</h3><p><strong>' + escape(lesson['idea']) + '</strong></p>' + paragraphs(lesson['teach']) +
            '<section class="course-lesson-model" aria-labelledby="course-lesson-model"><h3 id="course-lesson-model">2. Follow a worked example</h3>' + case_display(lesson['worked'], card_renderer) + paragraphs(lesson['worked']['answer']) + position_orders(lesson['worked'].get('table')) + '</section>'
            '<section class="course-lesson-attempt" aria-labelledby="course-lesson-try"><h3 id="course-lesson-try">3. Explain a changed situation</h3>' + case_display(attempt, card_renderer) +
            '<p><strong>Your task:</strong> ' + escape(attempt['prompt']) + '</p><p>Say your explanation or write it on paper before opening the answer.</p>'
            '<details class="poker-details" id="course-lesson-answer"><summary>Check your explanation</summary><div>' + paragraphs(attempt['answer']) + position_orders(attempt.get('table')) +
            '<p><a href="' + escape(attempt['repair'], quote=True) + '">Revisit the exact explanation</a> if your reason differed, then close this answer and explain what changed.</p></div></details></section>'
            '<p class="course-lesson-recall"><strong>Before you move on:</strong> ' + escape(lesson['recall']) + ' If that is still difficult, use the repair link or pause and return. Your explanation stays with you.</p>'
            '<nav class="course-lesson-next" aria-label="Continue from the short lesson"><a class="button" href="' + escape(next_route, quote=True) + '">' + escape(next_label) + '</a><a href="#lesson-reference">Read the full explanation</a></nav>'
            '<details class="poker-details course-lesson-options"><summary>Full explanation and other practice</summary><div>' + optional + '</div></details>'
            '<p class="editorial-note">Updated ' + stamp + ': ' + escape(revision) + ' Prepared with AI assistance. All scenes are fictional teaching examples. This is a self-check, not a skill score or betting recommendation.</p>')
