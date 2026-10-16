"""A coherent beginner route and one progressively revealed fictional hand."""
from html import escape
from hashlib import sha256
from pathlib import Path
import json
import re
import poker_practice
import poker_lessons

ROUTE = '/poker/free-poker-learning-path/'
DATA = '_source/poker/beginner-course.json'
CSS = 'assets/poker-course.css'
SCRIPT = 'assets/poker-course.js'
LESSONS = (
    ('first-decisions', 'Cards, actions and the pot'),
    ('starting-hand-decisions', 'Your starting hand in context'),
    ('first-flop-decisions', 'Your first decisions after the flop'),
    ('turn-and-river-decisions', 'The turn, river and showdown'),
    ('ranges-for-beginners', 'Your first range'),
    ('betting-with-a-purpose', 'Betting with a purpose'),
)


def load(root):
    data = json.loads((root / DATA).read_text(encoding='utf-8'))
    if data.get('version') != 1 or [(r['slug'], r['title']) for r in data['lessons']] != list(LESSONS):
        raise ValueError('Beginner course must contain the six published stages in order')
    for lesson in data['lessons']:
        source = (root / '_source/poker' / (lesson['slug'] + '.html')).read_text(encoding='utf-8')
        ids = set(re.findall(r'\bid="([^"]+)"', source))
        if not lesson['goal'].strip() or not lesson['recall'].strip():
            raise ValueError('Every stage needs an observable goal and a recall prompt')
        for anchor, label in lesson['first_pass']:
            if anchor not in ids or not label.strip():
                raise ValueError('First-pass links must reach existing lesson sections')
        route, anchor = lesson['practice'].split('#')
        if route != '/poker/beginner-checkpoint/' or 'id="' + anchor + '"' not in (root / '_source/poker/beginner-checkpoint.html').read_text():
            raise ValueError('Every stage needs a specific published practice situation')
    hand = data['hand']
    cards = hand['hero'] + hand['opponent'] + hand['board']
    if len(cards) != 9 or len(set(cards)) != 9 or any(not re.fullmatch(r'[2-9TJQKA][shdc]', c) for c in cards):
        raise ValueError('The practice hand needs nine distinct standard cards')
    ids = set()
    for scene in hand['scenes']:
        if not re.fullmatch(r'[a-z]+', scene['id']) or scene['id'] in ids:
            raise ValueError('Practice scenes need unique stable IDs')
        ids.add(scene['id'])
        if len(scene['choices']) != 3 or type(scene['correct']) is not int or scene['correct'] not in range(3):
            raise ValueError('A practice scene needs three explained choices and one answer')
        if scene['board_count'] not in [0, 3, 4, 5] or any(type(scene[k]) is not int or scene[k] < 0 for k in ['pot', 'hero_behind', 'opponent_behind']):
            raise ValueError('Practice states need valid cards and nonnegative counters')
        route, anchor = scene['repair'].split('#')
        slug = route.removeprefix('/poker/').strip('/')
        if slug not in dict(LESSONS) or 'id="' + anchor + '"' not in (root / '_source/poker' / (slug + '.html')).read_text():
            raise ValueError('Practice repairs must reach published lesson sections')
    if len(ids) != 6:
        raise ValueError('The guided hand requires six scenes')
    return data


def cards(values):
    ranks = {'A':'Ace', 'K':'King', 'Q':'Queen', 'J':'Jack', 'T':'Ten', **dict(zip('23456789', ['Two','Three','Four','Five','Six','Seven','Eight','Nine']))}
    suits = {'s':('spades','♠'), 'h':('hearts','♥'), 'd':('diamonds','♦'), 'c':('clubs','♣')}
    return '<span class="viewer-cards">' + ''.join(
        f'<span class="viewer-card{" viewer-card-red" if c[1] in "hd" else ""}" role="img" aria-label="{ranks[c[0]]} of {suits[c[1]][0]}"><span aria-hidden="true">{c[0]}<small>{suits[c[1]][1]}</small></span></span>' for c in values) + '</span>'


def syllabus(root):
    """The homepage uses the same lesson order and goals as the course itself."""
    return '<ol class="poker-foundations-syllabus">' + ''.join(
        '<li><a href="/poker/' + lesson['slug'] + '/">' + escape(lesson['title']) + '</a>'
        '<p>' + escape(lesson['goal']) + '</p></li>'
        for lesson in load(root)['lessons']) + '</ol>'


def guided_hand(root):
    data = load(root)['hand']
    scenes = []
    for number, scene in enumerate(data['scenes'], 1):
        sid = 'course-scene-' + scene['id']
        board = cards(data['board'][:scene['board_count']]) if scene['board_count'] else '<span>No shared cards yet.</span>'
        opponent = '<div><p class="course-state-label">Opponent at showdown</p>' + cards(data['opponent']) + '</div>' if scene.get('show_opponent') else ''
        options = ''.join(f'<li><label for="{sid}-{i}"><input hidden type="radio" id="{sid}-{i}" name="{sid}" value="{i}"> <span>{escape(label)}</span></label></li>' for i, (label, _) in enumerate(scene['choices']))
        notes = ''.join(f'<p class="course-choice-note" data-choice-note="{i}"><strong>{chr(65+i)}.</strong> {escape(feedback)}</p>' for i, (_, feedback) in enumerate(scene['choices']))
        extra = '<p>' + escape(scene['extra']) + '</p>' if scene.get('extra') else ''
        seats = ('<ol class="course-seat-order" aria-label="Initial preflop order"><li>First seat: folded</li><li>Next seat: folded</li><li>Cutoff: folded</li><li><strong>Button: you</strong></li><li>Small blind: posted 1</li><li>Big blind: posted 2</li></ol>' if number == 1 else '')
        scenes.append(f'<li id="{sid}" class="course-scene" data-course-scene data-answer="{scene["correct"]}">'
                      f'<h3 tabindex="-1">{number}. {escape(scene["title"])}</h3><p>{escape(scene["action"])}</p>{seats}'
                      '<div class="course-state"><div><p class="course-state-label">Your private cards</p>' + cards(data['hero']) + '</div><div><p class="course-state-label">Shared board</p>' + board + '</div>' + opponent + '</div>'
                      f'<dl class="course-counters"><div><dt>Pot now</dt><dd>{scene["pot"]}</dd></div><div><dt>Your stack behind</dt><dd>{scene["hero_behind"]}</dd></div><div><dt>Big blind behind</dt><dd>{scene["opponent_behind"]}</dd></div></dl>'
                      f'<fieldset class="course-question"><legend>{escape(scene["question"])}</legend><ol type="A">{options}</ol></fieldset>'
                      '<p class="course-manual-help">Say your answer and the reason, then reveal the explanation.</p>'
                      '<div class="course-check-controls" data-course-enhanced hidden><button type="button" data-course-check>Check answer</button><button type="button" data-course-retry>Try this scene again</button></div>'
                      '<p class="course-answer-status" data-course-status role="status" aria-live="polite"></p>'
                      '<details class="poker-details" data-course-solution><summary>Explanation and a repair link</summary><div>'
                      f'<p>{escape(scene["solution"])}</p>{notes}{extra}<p><a href="{escape(scene["repair"], quote=True)}">Revisit the exact lesson section</a>.</p></div></details></li>')
    return ('<section id="first-hand-practice" class="course-hand" aria-labelledby="course-hand-title" data-course-hand>'
            '<h2 id="course-hand-title">Follow one hand, one decision at a time.</h2>'
            '<p>Use counters or paper. The actions are scripted to explain the rules and accounting; they are not betting recommendations. Read a scene, give your reason, then compare it with the explanation. You can continue after any answer.</p>'
            '<p><a href="#beginner-practice">Skip to the six-stage lesson map</a>. No account or wager is needed.</p>'
            '<p class="course-scene-progress" data-course-progress aria-live="polite">Six scenes, from the first action to the result.</p>'
            '<ol class="course-scenes">' + ''.join(scenes) + '</ol>'
            '<nav class="course-hand-controls" aria-label="Guided hand scenes" data-course-enhanced hidden><button type="button" data-course-back>Previous scene</button><button type="button" data-course-next disabled>Next scene</button></nav>'
            '<p data-course-finish hidden>You reached the final scene. <a href="#beginner-practice">Choose the first unfamiliar stage below</a>, then <a href="/poker/beginner-checkpoint/">try a different situation</a>. A familiar answer is a cue to explain the reason again later.</p></section>')


def lesson_support(page, body, root):
    routes = load(root)['lessons']
    lesson = next((r for r in routes if page['path'] == '/poker/' + r['slug'] + '/'), None)
    if lesson is None:
        return body
    index = routes.index(lesson)
    links = ''.join(f'<li><a href="#{anchor}">{escape(label)}</a></li>' for anchor, label in lesson['first_pass'])
    card_case = {'first-decisions':'pair', 'first-flop-decisions':'three-kind', 'turn-and-river-decisions':'two-pair'}.get(lesson['slug'])
    card_practice = f'<p><a href="{ROUTE}#hand-lab-{card_case}">Build the best five with actual cards</a>. Choose the five yourself and explain what you leave out.</p>' if card_case else ''
    round_case = {"first-decisions":"preflop", "starting-hand-decisions":"preflop", "first-flop-decisions":"flop"}.get(lesson["slug"])
    round_practice = f'<p><a href="{ROUTE}#round-practice-{round_case}">Rehearse the actions with counters</a>. Choose the moves yourself and track who still needs a turn.</p>' if round_case else ''
    next_route = '/poker/' + routes[index+1]['slug'] + '/' if index+1 < len(routes) else '/poker/beginner-checkpoint/'
    next_label = 'Next lesson: ' + routes[index+1]['title'] if index+1 < len(routes) else 'Next: try the beginner checkpoint'
    optional = (f'<p>Use a full section when it answers your question:</p><ul>{links}</ul>'
                f'<p>Choose one extra practice task when useful.</p>{card_practice}{round_practice}'
                f'<p><a href="{poker_practice.lesson_link(lesson["slug"])}">See another worked example, then try three changed questions</a>.</p>'
                f'<p><a href="{lesson["practice"]}">Try this stage’s fresh practice situation</a>. Explain it before opening the answer.</p>')
    short = poker_lessons.load(root, [r['slug'] for r in routes])[index]
    first = ('<section class="course-first-pass" aria-labelledby="course-first-pass-title"><h2 id="course-first-pass-title">Start with the short lesson.</h2>'
             f'<p><strong>Stage {index+1} of 6:</strong> {escape(lesson["goal"])}</p>'
             + poker_lessons.render(short, cards, next_route, next_label, optional, page['revision']) + '</section>'
             '<h2 id="lesson-reference">Full explanation and more examples</h2>')
    anchor = '<p class="article-lead">'
    if body.count(anchor) != 1 or 'id="course-first-pass-title"' in body:
        raise ValueError('A course lesson needs one introduction and one first-pass guide')
    body = body.replace(anchor, first + anchor, 1)
    next_label = 'Next stage: ' + routes[index+1]['title'] if index+1 < len(routes) else 'Next: try the beginner checkpoint'
    prev_route = '/poker/' + routes[index-1]['slug'] + '/' if index else ROUTE
    end = ('<aside class="course-stage-end" aria-labelledby="course-stage-end-title"><h2 id="course-stage-end-title">Pause, explain, then choose the next step</h2>'
           f'<p>Close the explanation and try this from memory: {escape(lesson["recall"])}</p>'
           f'<p>Compare your reason with <a href="{lesson["practice"]}">a fresh practice situation</a>. If a part is unclear, use its repair link and return later.</p>'
           f'<nav aria-label="Continue the six-stage course"><a class="button" href="{next_route}">{escape(next_label)}</a><a href="{prev_route}">Previous stage or course overview</a><a href="{ROUTE}#beginner-practice">Six-stage map</a></nav></aside>')
    anchor = '<nav class="article-navigation"'
    if body.count(anchor) != 1:
        raise ValueError('A course lesson needs one original continuation')
    return body.replace(anchor, end + anchor, 1)


def workbook(root):
    data = load(root)
    short_lessons = poker_lessons.load(root, [r['slug'] for r in data['lessons']])
    lines = ['BEGINNER POKER STUDY CARD', 'Nolan Kido | https://nolankido.com' + ROUTE + '#beginner-practice', '',
             'For private notes with paper, a deck or counters. No wager or account needed.',
             'The website does not receive this file or save your progress.',
             'Use learning materials before or after play, following the room’s rules.',
             'Card codes: T=ten, J=jack, Q=queen, K=king, A=ace; s=spades, h=hearts,',
             'd=diamonds, c=clubs. Qh means queen of hearts. Each code names one card.', '',
             'MY NEXT SMALL STEP', 'The lesson I reached:', 'What I can explain without looking:',
             'One thing to revisit:', 'The exact lesson or section link I want to return to:', '',
             'OPTIONAL BETTING ROUND NOTES', 'https://nolankido.com/poker/free-poker-learning-path/#betting-rehearsal',
             'Starting point and street:', 'Seat acting now:', 'Total wager on this round:',
             'This seat already paid on this round:', 'My action and extra counters:',
             'Who still needs a turn, and why:', 'One rule to explain again later:', '',
             'SIX CONNECTED STAGES', 'Mark a box when you can explain a changed example. This is not a grade.', '']
    for number, lesson in enumerate(data['lessons'], 1):
        short = short_lessons[number - 1]
        lines += [f'[ ] {number}. {lesson["title"].upper()}', 'https://nolankido.com/poker/' + lesson['slug'] + '/', lesson['goal'],
                  'First pass: ' + '; '.join(label for _, label in lesson['first_pass']),
                  'SHORT LESSON: EXPLAIN A CHANGED SITUATION', *short['attempt']['setup'],
                  *[g['label'] + ': ' + ', '.join(g['values']) for g in short['attempt'].get('cards', []) + short['attempt'].get('candidates', [])],
                  short['attempt']['prompt'], 'My first explanation before checking:',
                  'Compare: https://nolankido.com/poker/' + lesson['slug'] + '/#course-lesson-try',
                  'My explanation after checking:', 'One difference I can explain with the answer closed:',
                  'Recall: ' + lesson['recall'], 'Fresh practice: https://nolankido.com' + lesson['practice'],
                  'My explanation:', 'Still unclear:', 'One correction after checking:', '']
    lines += ['ONE SCRIPTED HAND', 'Six players start with 100 counters. Blinds 1/2. No ante, fees or side pots.',
              'You are on the button with ace of hearts and jack of hearts.', 'The actions are supplied for learning, not betting recommendations.', '']
    for number, scene in enumerate(data['hand']['scenes'], 1):
        lines += [f'{number}. {scene["title"]}', scene['action'], scene['question'],
                  'My first reason:', 'One thing I corrected:', 'Repair: https://nolankido.com' + scene['repair'], '']
    lines += ['RETURN LATER', 'At the next study session, explain two checkpoint situations with the lesson closed.',
              'On a later day, try their changed situations. Use one repair link for any gap.',
              'This is a suggested routine, not a tested optimal poker-study schedule.',
              'Date I returned:', 'What I could explain without looking:', 'One question for the next visit:', '',
              'Completing this card does not establish profitable play or readiness to risk money.',
              'Fictional practice is enough. Do not upload private hand notes or identifying information.',
              'Prepared with AI assistance. October 15, 2026. Blank educational worksheet.', '']
    return '\n'.join(lines)


def overview(root, source):
    marker = '<!-- Course workbook preview -->'
    if source.count(marker) != 1:
        raise ValueError('Course overview needs one workbook preview marker')
    preview = '<details class="poker-details" id="course-workbook-preview"><summary>Preview the complete blank study card</summary><div><pre class="worksheet-preview">' + escape(workbook(root)) + '</pre></div></details>'
    return source.replace(marker, preview, 1)


def head(page, root):
    routes = {ROUTE} | {'/poker/' + slug + '/' for slug, _ in LESSONS}
    if page['path'] not in routes:
        return ''
    version = sha256((root / CSS).read_bytes()).hexdigest()[:12]
    extra = f'\n  <link rel="stylesheet" href="/{CSS}?v={version}">'
    if page['path'] == ROUTE:
        version = sha256((root / SCRIPT).read_bytes()).hexdigest()[:12]
        extra += f'\n  <script defer src="/{SCRIPT}?v={version}"></script>'
    return extra
