"""Six short worked examples and eighteen reviewed beginner practice questions."""
from hashlib import sha256
from html import escape
from pathlib import Path
import json
import re

ROUTE = '/poker/beginner-practice/'
DATA = '_source/poker/beginner-practice.json'
SOURCE = '_source/poker/beginner-practice.html'
CSS = 'assets/poker-beginner-practice.css'
SCRIPT = 'assets/poker-beginner-practice.js'
UNITS = ('calls', 'position', 'flop', 'river', 'ranges', 'purpose')
LESSONS = ('first-decisions', 'starting-hand-decisions', 'first-flop-decisions',
           'turn-and-river-decisions', 'ranges-for-beginners', 'betting-with-a-purpose')


def lesson_link(slug):
    return ROUTE + '#practice-' + UNITS[LESSONS.index(slug)]


def load(root):
    data = json.loads((root / DATA).read_text(encoding='utf-8'))
    if data.get('version') != 1 or [(u['id'], u['lesson']) for u in data['units']] != list(zip(UNITS, LESSONS)):
        raise ValueError('Practice requires six ordered skills matching the course')
    seen = set()
    for unit in data['units']:
        if len(unit['cases']) != 3:
            raise ValueError('Every skill needs three different questions')
        for record in [unit['example'], *unit['cases']]:
            for key in ['prompt', 'reason']:
                if not isinstance(record.get(key), str) or not record[key].strip():
                    raise ValueError('Practice needs a prompt and an explanation')
            hero, opponent, board = [record.get(k, []) for k in ['hero', 'opponent', 'board']]
            cards = hero + opponent + board
            if (cards and (len(hero) != 2 or len(opponent) not in [0, 2] or len(board) not in [3, 4, 5])) or len(set(cards)) != len(cards) or any(not re.fullmatch(r'[2-9TJQKA][shdc]', c) for c in cards):
                raise ValueError('Practice cards must be distinct standard cards in valid groups')
        for case in unit['cases']:
            if not re.fullmatch(r'[a-z]+(?:-[a-z]+)*', case['id']) or case['id'] in seen:
                raise ValueError('Practice questions need distinct stable IDs')
            seen.add(case['id'])
            if len(case['choices']) != 3 or type(case['correct']) is not int or case['correct'] not in range(3) or any(len(c) != 2 or not all(isinstance(s, str) and s.strip() for s in c) for c in case['choices']):
                raise ValueError('Each question needs three explained choices and one answer')
            route, anchor = case['repair'].split('#')
            slug = route.removeprefix('/poker/').strip('/')
            if slug not in LESSONS or not re.fullmatch(r'[a-z]+(?:-[a-z]+)*', anchor) or 'id="' + anchor + '"' not in (root / '_source/poker' / (slug + '.html')).read_text():
                raise ValueError('Repair links must reach real beginner lesson sections')
    return data


def card_state(record):
    from poker_course import cards
    if not record.get('hero'):
        return ''
    first_label = 'First private hand' if record.get('opponent') else 'Your private cards'
    values = [('hero', first_label), ('opponent', 'Second private hand (shown)'), ('board', 'Shared board')]
    return '<div class="drill-card-state">' + ''.join('<div><p class="drill-card-label">' + label + '</p>' + cards(record[key]) + '</div>' for key, label in values if record.get(key)) + '</div>'


def render(root):
    data = load(root)
    units = []
    links = ''.join(f'<a href="#practice-{u["id"]}" data-drill-skill="{u["id"]}">{escape(u["title"])}</a>' for u in data['units'])
    for number, unit in enumerate(data['units'], 1):
        model = unit['example']
        example = ('<details class="poker-details drill-model" data-drill-model open><summary>Learn the idea and see a worked example</summary><div>'
                   f'<p>{escape(unit["rule"])}</p><p><strong>Worked example:</strong> {escape(model["prompt"])}</p>' + card_state(model) +
                   f'<p>{escape(model["reason"])}</p><p><a href="/poker/{unit["lesson"]}/">Read the full stage explanation</a>.</p></div></details>')
        cases = []
        for case in unit['cases']:
            ident = 'exercise-' + case['id']
            choices = ''.join(f'<li><label for="{ident}-{i}"><input hidden type="radio" id="{ident}-{i}" name="{ident}" value="{i}"><span>{escape(label)}</span></label></li>' for i, (label, _) in enumerate(case['choices']))
            notes = ''.join(f'<p data-drill-note="{i}"><strong>{chr(65+i)}.</strong> {escape(note)}</p>' for i, (_, note) in enumerate(case['choices']))
            cases.append(f'<article class="drill-case" id="{ident}" data-drill-case data-answer="{case["correct"]}">'
                         f'<h3 tabindex="-1">{escape(case["title"])}</h3><p>{escape(case["prompt"])}</p>' + card_state(case) +
                         f'<fieldset><legend>{escape(case["question"])}</legend><p class="drill-think">Say an answer and its reason before looking at the choices.</p>'
                         '<button type="button" data-drill-choices-button data-drill-enhanced hidden>Show choices</button>'
                         f'<ol type="A" data-drill-choices>{choices}</ol></fieldset>'
                         '<p class="drill-native-help">Compare your own explanation with the answer panel below.</p>'
                         '<div class="drill-checks" data-drill-enhanced hidden><button type="button" data-drill-check>Check answer</button><button type="button" data-drill-unsure>I’m not sure</button><button type="button" data-drill-retry>Try this question again</button></div>'
                         '<p data-drill-status role="status" aria-live="polite"></p>'
                         '<details class="poker-details" data-drill-answer><summary>Explanation and the exact lesson to revisit</summary><div>'
                         f'<p>{escape(case["reason"])}</p>{notes}<p><a data-drill-repair href="{case["repair"]}">Revisit the exact lesson section</a>.</p></div></details></article>')
        units.append(f'<section class="drill-unit" id="practice-{unit["id"]}" data-drill-unit="{unit["id"]}" aria-labelledby="practice-{unit["id"]}-title">'
                     f'<h2 id="practice-{unit["id"]}-title" tabindex="-1">{number}. {escape(unit["title"])}</h2>{example}'
                     '<button type="button" data-drill-example-button data-drill-enhanced hidden>See the worked example</button>' + ''.join(cases) + '</section>')
    return ('<section class="drill-room" aria-labelledby="practice-room-title" data-drill-room>'
            '<h2 id="practice-room-title">Choose one idea to practice</h2>'
            '<nav class="drill-skill-nav" aria-label="Beginner practice skills">' + links + '</nav>'
            '<div class="drill-mix-controls" data-drill-enhanced hidden><button type="button" data-drill-mix>Try a mixed set without the examples</button>'
            '<p>Each mixed set has one question per skill. There are three fixed sets, then the questions repeat. You can open an example when you need one.</p></div>'
            '<p class="drill-progress" data-drill-progress aria-live="polite">Six skills, with one worked example and three questions each.</p>' + ''.join(units) +
            '<nav class="drill-steps" aria-label="Practice questions" data-drill-enhanced hidden><button type="button" data-drill-back disabled>Previous question</button><button type="button" data-drill-next disabled>Next question</button></nav>'
            '<section class="drill-review" data-drill-summary hidden aria-labelledby="practice-review-title"><h2 id="practice-review-title" tabindex="-1">Choose what to revisit</h2>'
            '<p>Use these notes about this visit to pick one idea to explain again later. A matching choice still needs a reason in your own words.</p><ul data-drill-review-list></ul>'
            '<p>Keep one gap and its lesson link on your <a href="/downloads/poker-beginner-study-card.txt" download>private study card</a>. The <a href="/poker/beginner-checkpoint/">beginner checkpoint</a> offers separate situations to try later.</p></section></section>')


def head(page, root):
    if page['path'] != ROUTE:
        return ''
    return ''.join((f'\n  <link rel="stylesheet" href="/{CSS}?v={sha256((root / CSS).read_bytes()).hexdigest()[:12]}">',
                    f'\n  <script defer src="/{SCRIPT}?v={sha256((root / SCRIPT).read_bytes()).hexdigest()[:12]}"></script>'))
