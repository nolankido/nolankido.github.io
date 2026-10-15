"""Rehearse complete betting rounds inside the existing free course."""
from hashlib import sha256
from html import escape
import json

ROUTE = '/poker/free-poker-learning-path/'
DATA = '_source/poker/round-practice.json'
CSS = 'assets/poker-round-practice.css'
SCRIPT = 'assets/poker-round-practice.js'
IDS = ('preflop', 'flop', 'raise')


def load(root):
    data = json.loads((root / DATA).read_text())
    if data.get('version') != 1 or tuple(c['id'] for c in data['cases']) != IDS:
        raise ValueError('Round practice requires three reviewed starting points')
    for case in data['cases']:
        s = case['state']
        if not case['title'].strip() or not case['prompt'].strip() or s['street'] not in {'preflop','flop'}:
            raise ValueError('Each starting point needs its context')
        if [p['id'] for p in s['players']] != ['button','small','big'] or any(not p['name'].strip() or type(p['paid']) is not int or not 0 <= p['paid'] <= 1000 or type(p['folded']) is not bool for p in s['players']):
            raise ValueError('Use three distinct seats and whole counter payments')
        active = {p['id'] for p in s['players'] if not p['folded']}
        if len(active) < 2 or not s['pending'] or len(s['pending']) != len(set(s['pending'])) or not set(s['pending']) <= active:
            raise ValueError('Pending decisions must belong to remaining players')
        if any(type(s[k]) is not int or not 0 <= s[k] <= 1000 for k in ['priorPot','current','lastRaise','bigBlind']) or s['bigBlind'] != 2 or s['lastRaise'] < 2 or s['current'] != max(p['paid'] for p in s['players']):
            raise ValueError('The pot and last full raise must have consistent totals')
        if any(p['paid'] < s['current'] and p['id'] not in s['pending'] for p in s['players'] if not p['folded']):
            raise ValueError('Every unmatched player still needs a decision')
        if not case['worked'] or any(w['actor'] not in active or w['action'] not in {'check','bet','call','raise','fold'} or type(w['add']) is not int or w['add'] < 0 or not w['reason'].strip() for w in case['worked']):
            raise ValueError('Each starting point needs a complete worked line')
    return data


def table(state):
    rows = ''.join('<tr><th scope="row">' + escape(p['name']) + '</th><td>' + str(p['paid']) + '</td><td>' + ('Folded' if p['folded'] else 'Next to act' if p['id'] == state['pending'][0] else 'In the hand') + '</td></tr>' for p in state['players'])
    return '<table class="viewer-table round-table"><caption>Starting payments on this betting round</caption><thead><tr><th scope="col">Seat</th><th scope="col">Paid this round</th><th scope="col">Status</th></tr></thead><tbody>' + rows + '</tbody></table>'


def render(root):
    data = load(root)
    cases = []
    for c in data['cases']:
        names = {p['id']:p['name'] for p in c['state']['players']}
        line = ''.join('<li><strong>' + escape(names[w['actor']]) + ': ' + escape(w['action']) + ('; add ' + str(w['add']) if w['add'] else '') + '.</strong> ' + escape(w['reason']) + '</li>' for w in c['worked'])
        encoded = escape(json.dumps(c['state'],separators=(',',':')),quote=True)
        cases.append(f'<article id="round-practice-{c["id"]}" class="round-case" data-round-case data-round-state="{encoded}" aria-labelledby="round-practice-{c["id"]}-title"><h3 id="round-practice-{c["id"]}-title" tabindex="-1">{escape(c["title"])}</h3><p>{escape(c["prompt"])}</p>'
                     '<div class="round-native" data-round-native><p>Use counters or paper. Choose an action for the next seat, move only the extra counters, then name who still needs a turn. Compare with the worked line when ready.</p>' + table(c['state']) + '</div>'
                     '<div data-round-live hidden></div>'
                     '<details class="poker-details" data-round-worked><summary>See one worked line for this starting point</summary><div><ol>' + line + '</ol><p>This is one legal line. Other legal choices are possible, and none is graded as a good strategy.</p></div></details></article>')
    return ('<section class="round-practice" id="betting-rehearsal" aria-labelledby="round-practice-title" data-round-practice><h2 id="round-practice-title">Rehearse a betting round with counters.</h2>'
            '<p>Know the cards but lose track of the action? Take turns for all three seats. Choose an action and enter the counters to add. The pot, payments and next turn change with your choices. <strong>Try one round, then pause or continue to the lessons.</strong></p>'
            '<p>These are fictional rule exercises with no cards or recommended plays. Imagine every player has enough counters. Stack limits, all-ins, side pots, antes and fees are omitted. Amounts are whole counters, with a practice ceiling of 1,000 per player on this round. That ceiling is not a no-limit poker rule.</p>'
            '<details class="poker-details"><summary>Five actions, in plain language</summary><div><dl><dt>Check</dt><dd>Add nothing when you owe nothing. Keep your hand.</dd><dt>Bet</dt><dd>Open wagering on a postflop round. Here the opening bet is at least 2, the big blind.</dd><dt>Call</dt><dd>Match the current total wager. Add only the difference from what this seat paid on this round.</dd><dt>Raise</dt><dd>Increase the total wager by at least the last full bet or raise. The big blind is a live wager before the flop.</dd><dt>Fold</dt><dd>Give up the hand when facing a wager. Earlier payments stay in the pot. Use checking when you owe nothing in this exercise; folding when not facing a wager can violate live tournament procedure.</dd></dl><p>A round ends only when every remaining player has had its required turn and answered the latest wager. If only one player remains, the hand ends immediately. A check does not prevent another player from betting later.</p></div></details>'
            '<nav class="round-starts" aria-label="Betting rehearsal starting points">' + ''.join(f'<a href="#round-practice-{c["id"]}">{label}</a>' for c,label in zip(data['cases'],['Before the flop','A fresh flop','Facing a raise'])) + '</nav>' + ''.join(cases) +
            '<p class="round-privacy">Moves and review notes stay in this page and clear on reload. This exercise sends no answers and stores no progress. The worked lines and starting tables remain available without JavaScript and in print.</p>'
            '<p><a href="#beginner-practice">Next: choose a stage from the six-stage map</a>. For another explanation, read <a href="/poker/first-decisions/#legal-actions">the actions</a>, <a href="/poker/first-decisions/#turn-order">turn order</a> or <a href="/poker/first-decisions/#chips-owed">additional payments</a>.</p>'
            '<details class="poker-details"><summary>Rule sources and limits</summary><div><p>Checked October 15, 2026 against <a href="https://www.pokerstars.com/poker/games/texas-holdem/">PokerStars’ hold’em rules</a> and <a href="https://www.pokertda.com/view-poker-tda-rules/">Poker TDA’s 2026 rules</a>. This limited model does not reproduce venue procedures, short all-ins or strategy. A legal move is not evidence of a profitable move.</p></div></details></section>')


def head(page, root):
    if page['path'] != ROUTE:
        return ''
    return f'\n  <link rel="stylesheet" href="/{CSS}?v={sha256((root / CSS).read_bytes()).hexdigest()[:12]}">\n  <script defer src="/{SCRIPT}?v={sha256((root / SCRIPT).read_bytes()).hexdigest()[:12]}"></script>'
