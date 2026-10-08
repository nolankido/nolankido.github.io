"""Exact, fixed study examples, not a live-hand calculator or strategy chart."""
from fractions import Fraction
from html import escape
from pathlib import Path

SIZES = (('Quarter pot', Fraction(1, 4)), ('One-third pot', Fraction(1, 3)), ('Half pot', Fraction(1, 2)),
         ('Two-thirds pot', Fraction(2, 3)), ('Three-quarters pot', Fraction(3, 4)), ('Pot', Fraction(1)),
         ('One-and-a-half pot', Fraction(3, 2)), ('Twice pot', Fraction(2)))
SCOPE = ('Heads-up, first bet into the pot, no rake, no further betting, and no side pots. '
         'Call equity counts ties by their share of the pot. Pure bluffs lose every time they are called. '
         'These are chip-EV break-even thresholds, not recommendations to call or bluff. '
         'Use away from play; close the playing client when its policy requires it.')


def rows():
    return [(label, 100 * size / (1 + 2 * size), 100 * size / (1 + size)) for label, size in SIZES]


def supplement():
    body = ''.join(f'<tr><th scope="row">{label}</th><td>{float(call):.2f}%</td><td>{float(bluff):.2f}%</td></tr>' for label, call, bluff in rows())
    return {'poker_price_table': '<table class="viewer-table"><caption>Call equity and pure-bluff fold thresholds, rounded to two decimals</caption>'
            '<thead><tr><th scope="col">First bet size</th><th scope="col">Call equity</th><th scope="col">Folds for bluff</th></tr></thead><tbody>' + body + '</tbody></table>'}


def exports():
    lines = ['# Poker math quick reference', '', SCOPE, '', 'P = pot before a first bet; B = that bet.',
             'Call equity = B / (P + 2B).', 'Pure-bluff break-even fold rate = B / (P + B).', '',
             '| First bet size | Call equity | Folds for bluff |', '|---|---:|---:|']
    lines += [f'| {label} | {float(call):.2f}% | {float(bluff):.2f}% |' for label, call, bluff in rows()]
    lines += ['', 'For a general call: extra call / (current pot including all outstanding wagers + extra call).',
              'Use only the pot you can win; an all-in side-pot situation needs separate accounting.',
              'SPR = effective chips remaining / current pot, both measured at the same decision.',
              'Pot-limit raise: first account for the call, then a raise by the pot after that call.',
              'General pure-bluff threshold = incremental risk / (incremental risk + reward).',
              'Do not reuse a first-bet size table for a raise without recalculating risk and reward.',
              'Drawing to a hand is not the same as winning with it. Tournament payout effects are not included.', '',
              'Worked examples, assumptions and sources: https://nolankido.com/poker/poker-math-reference/',
              'Published October 8, 2026. Prepared with AI assistance. Fixed fictional study examples.', '']
    return {Path('downloads/poker-math-reference.md'): '\n'.join(lines)}
