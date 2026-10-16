"""Card foundations and constructive best-five practice within the free course."""
from hashlib import sha256
from html import escape
from pathlib import Path
import json
import re

ROUTE = '/poker/free-poker-learning-path/'
DATA = '_source/poker/hand-lab.json'
CSS = 'assets/poker-hand-lab.css'
SCRIPT = 'assets/poker-hand-lab.js'
IDS = ('pair', 'high-card', 'two-pair', 'three-kind', 'board-straight', 'flush',
       'full-house', 'four-kind', 'straight-flush', 'ace-low')
RANKS = dict(zip('23456789TJQKA', ['Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Jack','Queen','King','Ace']))
SUITS = {'s':('spades','♠'), 'h':('hearts','♥'), 'd':('diamonds','♦'), 'c':('clubs','♣')}


def load(root):
    data = json.loads((root / DATA).read_text(encoding='utf-8'))
    if data.get('version') != 1 or tuple(c['id'] for c in data['cases']) != IDS:
        raise ValueError('Hand lab needs the ten reviewed hands in order')
    for item in [data['example'], *data['cases']]:
        cards = item['hero'] + item['board']
        if len(item['hero']) != 2 or len(item['board']) != 5 or len(set(cards)) != 7 or any(not re.fullmatch(r'[2-9TJQKA][shdc]', c) for c in cards):
            raise ValueError('Hand lab requires two private and five distinct shared cards')
        if len(item['solution']) != 5 or len(set(item['solution'])) != 5 or not set(item['solution']) <= set(cards) or not item['reason'].strip():
            raise ValueError('A hand needs one five-card solution and its reason')
    for item in data['cases']:
        if type(item['category']) is not int or item['category'] not in range(9) or any(not item[k].strip() for k in ['title','prompt','hint']):
            raise ValueError('A hand needs a category, question and hint')
        route, anchor = item['repair'].split('#')
        if route not in {'/poker/hand-rankings/','/poker/first-decisions/','/poker/first-flop-decisions/'} or not re.fullmatch(r'[a-z]+(?:-[a-z]+)*', anchor) or 'id="' + anchor + '"' not in (root / '_source/poker' / (route.strip('/').split('/')[-1] + '.html')).read_text():
            raise ValueError('Hand repairs must reach an existing explanation')
    return data


def card_name(code):
    return RANKS[code[0]] + ' of ' + SUITS[code[1]][0]


def card_groups(item, ident=None):
    from poker_course import cards
    groups = []
    for key, label in [('hero', 'Your two private cards'), ('board', 'Five shared cards on the completed board')]:
        if ident is None:
            content = cards(item[key])
        else:
            content = '<div class="hand-lab-card-options">' + ''.join(
                f'<label class="hand-lab-card" for="{ident}-{code}"><input hidden type="checkbox" id="{ident}-{code}" data-card="{code}" aria-label="{card_name(code)}, {"private" if key == "hero" else "shared"} card">'
                f'<span class="viewer-card{" viewer-card-red" if code[1] in "hd" else ""}" aria-hidden="true">{code[0]}<small>{SUITS[code[1]][1]}</small></span><span class="hand-lab-card-name">{RANKS[code[0]]}<span class="visually-hidden"> of</span><br>{SUITS[code[1]][0]}</span></label>' for code in item[key]) + '</div>'
        label_id = f' id="{ident}-{key}"' if ident else ''
        groups.append(f'<div class="hand-lab-group"><p class="hand-lab-label"{label_id}>' + label + '</p>' + content + '</div>')
    return '<div class="hand-lab-card-groups">' + ''.join(groups) + '</div>'


def render(root):
    from poker_course import cards
    data = load(root)
    ranking_source = (root / '_source/poker/hand-rankings.html').read_text()
    ranking = re.search(r'<ol class="viewer-rankings">.*?</ol>', ranking_source, re.S)
    if ranking is None or ranking[0].count('data-rank-cards=') != 10:
        raise ValueError('Reuse the complete published visual ranking reference')
    model = data['example']
    example = '<details class="poker-details hand-lab-model" open><summary>See one worked selection first</summary><div>' + card_groups(model) + '<p><strong>One best five:</strong></p>' + cards(model['solution']) + f'<p>{escape(model["reason"])}</p></div></details>'
    cases = []
    for item in data['cases']:
        ident = 'hand-lab-' + item['id']
        cases.append(f'<article class="hand-lab-case" id="{ident}" aria-labelledby="{ident}-title" data-lab-case data-solution="{",".join(item["solution"])}"><h3 id="{ident}-title" tabindex="-1">{escape(item["title"])}</h3>'
                     f'<p>{escape(item["prompt"])}</p><fieldset><legend>Select exactly five cards, then explain your choice.</legend>' + card_groups(item, ident) + '</fieldset>'
                     '<p class="hand-lab-count" data-lab-count role="status"></p>'
                     '<div class="hand-lab-controls" data-lab-enhanced hidden><button type="button" data-lab-check>Check my five</button><button type="button" data-lab-clear>Clear this selection</button><button type="button" data-lab-show>Show one worked solution</button></div>'
                     '<p class="hand-lab-feedback" data-lab-feedback role="status" aria-live="polite"></p>'
                     '<details class="poker-details" data-lab-hint><summary>Hint for this hand</summary><div><p>' + escape(item['hint']) + '</p></div></details>'
                     '<details class="poker-details" data-lab-answer><summary>One strongest selection and why</summary><div>' + cards(item['solution']) +
                     f'<p>{escape(item["reason"])}</p><p>Different physical cards can make equally strong hands. Any selection with the same best five-card value is accepted.</p><p><a data-lab-repair href="{escape(item["repair"],quote=True)}">Review this rule in the full lesson</a>.</p></div></details></article>')
    return ('<section id="card-basics" class="hand-foundations" aria-labelledby="card-basics-title"><h2 id="card-basics-title">Start with the cards and the goal.</h2>'
            '<p>You win a hand when every other player folds, or by having the strongest five-card hand among players who reach the showdown. A tied best hand can share the pot. You do not have to bet on every turn to keep playing; the guided hand below explains the actions.</p>'
            '<p>A standard deck has 52 different cards: thirteen ranks in each of four suits. The usual high-to-low rank order is <strong>A K Q J T 9 8 7 6 5 4 3 2</strong>. A is ace, K king, Q queen, J jack and T ten. The four suits are spades ♠, hearts ♥, diamonds ♦ and clubs ♣. Suits do not outrank one another.</p>'
            '<p>You receive <strong>two private cards</strong>. The shared board arrives as three cards on the flop, one on the turn, then one on the river. Once all five shared cards are out, choose the strongest five from your seven available cards. Use zero, one or two private cards. An ace can be low in A-2-3-4-5, but a straight cannot wrap through K-A-2-3-4.</p>'
            '<details class="poker-details hand-lab-rankings"><summary>What beats what? Open the visual ranking reference</summary><div><p>Read strongest to weakest. A royal flush is the highest straight flush. Compare the hand category first, then the relevant ranks and kickers. There is no sixth-card tiebreaker.</p>' + ranking[0] +
            '<p><a href="/poker/hand-rankings/">Read the complete rankings and tie explanations</a>.</p></div></details>'
            '<p class="hand-basics-ready"><strong>Ready for the course?</strong> <a href="/poker/first-decisions/">Begin lesson 1</a> after these basics and the worked selection below. The ten changed hands are optional extra practice.</p>'
            '<section id="hand-lab" class="hand-lab" data-hand-lab aria-labelledby="hand-lab-title"><h2 id="hand-lab-title">Build the best five yourself.</h2>'
            '<p>First explain the worked example. Then choose five actual cards in each changed hand. Deselect a card to replace it. These ten fixed fictional hands repeat; they teach card selection on completed boards, not betting strategy or readiness to play for money.</p>' + example +
            '<p><strong>Try one hand, then pause.</strong> <a href="/poker/first-decisions/">Begin lesson 1</a>, or <a href="#first-hand-practice">follow a guided hand</a> when the actions need more explanation. Return to the other card-building hands when useful.</p>'
            '<p class="hand-lab-progress" data-lab-progress aria-live="polite">Ten hands to build, with explanations.</p>' + ''.join(cases) +
            '<nav class="hand-lab-steps" data-lab-enhanced hidden aria-label="Hand-building exercises"><button type="button" data-lab-back disabled>Previous hand</button><button type="button" data-lab-next disabled>Next hand</button></nav>'
            '<section class="hand-lab-review" data-lab-review hidden aria-labelledby="hand-lab-review-title"><h3 id="hand-lab-review-title" tabindex="-1">Choose a card rule to revisit</h3><p>These are notes about this visit, not a score or proof of learning. Keep one correction on your <a href="/downloads/poker-beginner-study-card.txt" download>private study card</a>, then build that hand again at a later visit.</p><ul data-lab-review-list></ul><button type="button" data-lab-restart>Practice these ten hands again</button></section>'
            '<p>Selections and review notes stay in this page and clear when it reloads. No answers are sent or saved by the hand lab. You can use a deck or paper and the native answer panels when the script is unavailable.</p></section>'
            '<p class="hand-foundations-next"><a class="button" href="/poker/first-decisions/">Begin lesson 1</a> <a href="#beginner-practice">Return to the six-lesson map</a></p></section>')


def head(page, root):
    if page['path'] != ROUTE:
        return ''
    return f'\n  <link rel="stylesheet" href="/{CSS}?v={sha256((root / CSS).read_bytes()).hexdigest()[:12]}">\n  <script defer src="/{SCRIPT}?v={sha256((root / SCRIPT).read_bytes()).hexdigest()[:12]}"></script>'
