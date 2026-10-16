"""Connected native course-finish attempts, with the same prompts on paper."""
from html import escape
import json
import re

DATA = '_source/poker/final-hands.json'
ROUTE = '/poker/beginner-checkpoint/'
SEATS = ['first seat', 'next seat', 'cutoff', 'button', 'small blind', 'big blind']


def load(root):
    data = json.loads((root / DATA).read_text(encoding='utf-8'))
    if data.get('version') != 1 or [h['id'] for h in data['hands']] != ['a', 'b']:
        raise ValueError('The final exercise needs two fixed, clearly identified hands')
    for hand in data['hands']:
        known = hand['hero'] + hand['board'] + hand['opponent']
        if [len(hand[k]) for k in ['hero', 'board', 'opponent']] != [2, 5, 2] or len(set(known)) != 9 or any(not re.fullmatch(r'[2-9TJQKA][shdc]', c) for c in known):
            raise ValueError('Each full hand needs nine distinct standard cards')
        if hand['hero_seat'] not in range(6) or hand['opponent_seat'] not in range(6) or hand['hero_seat'] == hand['opponent_seat']:
            raise ValueError('The two active seats must differ')
        if [s['board_count'] for s in hand['stops']] != [0, 3, 4, 5]:
            raise ValueError('Reveal only the board available on each betting round')
        previous = [0] * 6
        for stop in hand['stops']:
            paid = stop['paid']
            if len(paid) != 6 or any(type(n) is not int or not 0 <= n <= 100 for n in paid) or any(n < old for n, old in zip(paid, previous)):
                raise ValueError('Contributions must preserve the six original 100-chip stacks')
            previous = paid
            if any(type(stop[k]) is not int or stop[k] < 0 for k in ['street_paid', 'wager']) or stop['street_paid'] > stop['wager'] or stop['street_paid'] > paid[hand['hero_seat']]:
                raise ValueError('Current-round contributions must fit the wager and ledger')
            for key in ['setup', 'prompt']:
                if not isinstance(stop[key], str) or not stop[key].strip():
                    raise ValueError('Every stop needs the available facts and an open prompt')
            if not stop['answer'] or any(not p.strip() for p in stop['answer']):
                raise ValueError('Each open attempt needs explained feedback')
            for candidate in stop.get('candidates', []):
                cards = candidate['values']
                if len(cards) != 2 or len(set(cards)) != 2 or any(not re.fullmatch(r'[2-9TJQKA][shdc]', c) for c in cards):
                    raise ValueError('Candidate alternatives must be standard two-card holdings')
            if not stop['repairs']:
                raise ValueError('Feedback needs a precise repair')
            for url, label in stop['repairs']:
                route, anchor = url.split('#')
                source = root / '_source' / (route.strip('/') + '.html')
                if not label.strip() or not route.startswith('/poker/') or not source.is_file() or 'id="' + anchor + '"' not in source.read_text():
                    raise ValueError('Final-hand repairs must reach published lesson sections')
        final = hand['finish_paid']
        last = hand['stops'][-1]
        expected = list(last['paid'])
        expected[hand['hero_seat']] += last['wager'] - last['street_paid']
        if final != expected or any(n > 100 for n in final) or hand['winner_seat'] not in [hand['hero_seat'], hand['opponent_seat']]:
            raise ValueError('The final call and award must match the last ledger')
    return data['hands']


def paragraphs(values):
    return ''.join('<p>' + escape(value) + '</p>' for value in values)


def render(root, cards):
    hands = []
    for hand in load(root):
        hid = 'course-hand-' + hand['id']
        stops = []
        for number, stop in enumerate(hand['stops'], 1):
            sid = hid + '-' + stop['street'].lower()
            board = cards(hand['board'][:stop['board_count']]) if stop['board_count'] else '<p>No shared cards yet.</p>'
            groups = '<div class="course-lesson-cards"><div><p><strong>Your cards</strong></p>' + cards(hand['hero']) + '</div><div><p><strong>Shared board so far</strong></p>' + board + '</div></div>'
            if stop.get('candidates'):
                groups += '<p>Compare these separate candidate holdings. Their frequencies are not supplied.</p><div class="course-lesson-cards">' + ''.join('<div><p><strong>' + escape(c['label']) + '</strong></p>' + cards(c['values']) + '</div>' for c in stop['candidates']) + '</div>'
            counts = [('Pot now', sum(stop['paid'])), ('Your chips paid this round', stop['street_paid']), ('Wager to match this round', stop['wager'])]
            state = '<dl class="course-counters">' + ''.join('<div><dt>' + label + '</dt><dd>' + str(value) + '</dd></div>' for label, value in counts) + '</dl>'
            state += '<p>Counters behind: you ' + str(100 - stop['paid'][hand['hero_seat']]) + '; ' + SEATS[hand['opponent_seat']] + ' ' + str(100 - stop['paid'][hand['opponent_seat']]) + '.</p>'
            content = '<h4>' + str(number) + '. ' + stop['street'] + '</h4><p>' + escape(stop['setup']) + '</p>' + groups + state + '<p><strong>Explain before opening the feedback:</strong> ' + escape(stop['prompt']) + '</p>'
            content += '<details class="poker-details course-final-answer" id="' + sid + '-answer"><summary>Compare your ' + stop['street'].lower() + ' explanation</summary><div>' + paragraphs(stop['answer']) + '<p><strong>Repair the step that differed:</strong> ' + ' · '.join('<a href="' + escape(url, quote=True) + '">' + escape(label) + '</a>' for url, label in stop['repairs']) + '.</p></div></details>'
            if number == 1:
                stops.append('<section class="course-final-stop" id="' + sid + '">' + content + '</section>')
            else:
                stops.append('<details class="poker-details course-final-street" id="' + sid + '"><summary>Continue to the ' + stop['street'].lower() + ' after your explanation</summary><div>' + content + '</div></details>')
        ending = '<details class="poker-details course-final-ending" id="' + hid + '-ending"><summary>After all four explanations: reveal the scripted result</summary><div>' + cards(hand['opponent']) + paragraphs(hand['ending']) + '</div></details>'
        content = '<h3 id="' + hid + '-title">' + escape(hand['title']) + '</h3>' + ''.join(stops) + ending
        hands.append(('<section aria-labelledby="' + hid + '-title">' + content + '</section>') if hand['id'] == 'a' else '<details class="poker-details course-final-return" id="' + hid + '"><summary>On a later visit: try Hand B with the lessons closed</summary><div>' + content + '</div></details>')
    return ('<section class="course-final" aria-labelledby="course-hand"><h2 id="course-hand">Finish with a complete hand.</h2>'
            '<p>After the six lessons, close them and try Hand A. Say or write your reason at each stop before opening feedback. Then continue to the next street. Later cards and the result start closed so you can reason from what is known at that moment. These are fixed fictional lines, not recommended betting sequences.</p>'
            '<p>Both hands use six players, 100 counters each, blinds of 1 and 2, no antes, fees, side pots or prize effects. Clockwise preflop order: first seat, next seat, cutoff, button, small blind, big blind. Each hand starts fresh. A pot shown at a decision includes chips already wagered.</p>'
            '<p><a href="/downloads/poker-beginner-study-card.txt" download>Keep the prompts in the study card (TXT)</a> or use paper. Keep your first explanation, one correction and one question. Answers stay with you; this exercise has no form, saved progress or automatic grade. Opening a panel does not establish that you understood it.</p>'
            + ''.join(hands) +
            '<h3 id="course-hand-review">Choose your next step from your explanations</h3><ul><li><strong>Lost the action or chips?</strong> Use the repair at that stop, then reconstruct the contributions without looking.</li><li><strong>Mixed up cards, draws or possible holdings?</strong> Rebuild the five cards and explain which fact ruled a candidate in or out.</li><li><strong>Named a price or a bet without its assumptions?</strong> State the missing range or responses before choosing an action.</li><li><strong>Could explain Hand A?</strong> Pause, then try Hand B at a later study session with these explanations closed. Its position, completed draw and price change. Repeating these two fixed hands eventually becomes recall; use unfamiliar examples to check further transfer.</li></ul>'
            '<p>Write: “Without looking, I could explain ___; I corrected ___; next I will revisit ___.” Use the <a href="#next-step">six-skill repair table</a> or the individual questions below for focused practice. These examples do not establish profitable play or readiness to risk money.</p></section>')


def workbook(root):
    lines = ['', 'CONNECTED FINAL HANDS', 'Attempt Hand A after the six lessons. Try Hand B on a later visit.',
             'Explain each stop before looking at feedback or later streets.',
             'Six players each start with 100 counters, blinds 1/2, no antes, fees or prize effects.',
             'Seat order: first seat, next seat, cutoff, button, small blind, big blind.',
             'Card codes: A ace, K king, Q queen, J jack, T ten; h hearts, d diamonds, c clubs, s spades.',
             'The scripted actions are teaching facts, not recommended strategy. These two hands are fixed.', '']
    for hand in load(root):
        lines += [hand['title'], 'Your cards: ' + ' '.join(hand['hero'])]
        for stop in hand['stops']:
            anchor = 'course-hand-' + hand['id'] + '-' + stop['street'].lower()
            lines += ['', stop['street'], stop['setup'], 'Board so far: ' + (' '.join(hand['board'][:stop['board_count']]) or 'none'),
                      'Pot now: ' + str(sum(stop['paid'])) + '; your chips paid this round: ' + str(stop['street_paid']) + '; wager to match: ' + str(stop['wager'])]
            for candidate in stop.get('candidates', []):
                lines.append(candidate['label'] + ': ' + ' '.join(candidate['values']))
            lines += [stop['prompt'], 'My first explanation:', 'One correction after comparing:', 'Compare: https://nolankido.com' + ROUTE + '#' + anchor + '-answer']
        lines += ['', 'My explanation before the result:', 'The result did or did not support my original assumptions because:',
                  'Reveal only afterward: https://nolankido.com' + ROUTE + '#course-hand-' + hand['id'] + '-ending', '']
    lines += ['Without looking, I could explain:', 'One repair and the section to revisit:', 'On my later attempt, what changed:',
              'These are self-check notes, not a skill score. No answers are sent to the website.', '']
    return '\n'.join(lines)
