from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label}, found {count}")
    return text.replace(old, new, 1)


RANK_NAMES = {
    "2": "Two", "3": "Three", "4": "Four", "5": "Five", "6": "Six",
    "7": "Seven", "8": "Eight", "9": "Nine", "T": "Ten", "J": "Jack",
    "Q": "Queen", "K": "King", "A": "Ace",
}
SUIT_NAMES = {"s": "spades", "h": "hearts", "d": "diamonds", "c": "clubs"}
SUIT_SYMBOLS = {"s": "♠", "h": "♥", "d": "♦", "c": "♣"}


def card(code):
    rank, suit = code
    red = " viewer-card-red" if suit in "hd" else ""
    face = "10" if rank == "T" else rank
    return (
        f'<span class="viewer-card{red}" data-card="{code}" role="img" '
        f'aria-label="{RANK_NAMES[rank]} of {SUIT_NAMES[suit]}">'
        f'<span aria-hidden="true">{face}<small>{SUIT_SYMBOLS[suit]}</small></span></span>'
    )


def best_group(player, cards):
    codes = " ".join(cards)
    rendered = "".join(card(code) for code in cards)
    return (
        f'<div class="viewer-card-group viewer-best-five-group" data-player="{player.lower()}" '
        f'data-best-cards="{codes}"><p class="viewer-card-label">Player {player}\'s best five</p>'
        f'<div class="viewer-cards">{rendered}</div></div>'
    )


def recap(first, second):
    return (
        '<div class="viewer-board-grid viewer-best-five">'
        + best_group("A", first)
        + best_group("B", second)
        + "</div>"
    )


source_path = ROOT / "_source/poker/hand-rankings.html"
source = source_path.read_text(encoding="utf-8")
answers = [
    (
        "The kicker counts",
        "A wins: Q-Q-A-9-7 beats Q-Q-J-9-7. The pair is equal; the first different kicker decides.",
        ["Qs", "Qd", "As", "9h", "7c"],
        ["Qh", "Qd", "Jh", "9h", "7c"],
    ),
    (
        "The board supplies everything",
        "Tie. Both play A-A-K-K-Q from the board. None of their hole cards improves those five, and there is no sixth-card tiebreaker.",
        ["Ah", "Ad", "Kc", "Kd", "Qs"],
        ["Ah", "Ad", "Kc", "Kd", "Qs"],
    ),
    (
        "Full house versus full house",
        "A wins with aces full of kings, A-A-A-K-K. B has kings full of aces, K-K-K-A-A. Compare the three matching cards before comparing the pair.",
        ["As", "Ah", "Ad", "Kc", "Kd"],
        ["Ks", "Kc", "Kd", "Ah", "Ad"],
    ),
    (
        "The ace is low this time",
        "B wins with a seven-high straight, 3-4-5-6-7. A has the five-high wheel, A-2-3-4-5. The ace is functioning as a one, not a high-card tiebreaker.",
        ["As", "2d", "3s", "4h", "5d"],
        ["3s", "4h", "5d", "6c", "7c"],
    ),
]
for title, explanation, first, second in answers:
    old = (
        f'<details class="poker-details viewer-question"><summary>Reveal the winner: {title}</summary>'
        f'<div><p>{explanation}</p></div></details>'
    )
    new = (
        f'<details class="poker-details viewer-question"><summary>Reveal the winner: {title}</summary>'
        f'<div>{recap(first, second)}<p>{explanation}</p></div></details>'
    )
    source = replace_once(source, old, new, f"answer for {title}")
source_path.write_text(source, encoding="utf-8")


test_path = ROOT / "_tests/test_viewer_guides.py"
test_text = test_path.read_text(encoding="utf-8")
parser_code = '''\n\nclass BestFiveGroups(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.groups=[]; self.current=None; self.depth=0; self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs); classes=set(attrs.get('class','').split())
        if self.current is None and tag=='div' and 'viewer-best-five-group' in classes:
            self.current={'player':attrs['data-player'],'declared':attrs['data-best-cards'],'cards':[]}
            self.depth=1
            return
        if self.current is not None:
            if tag=='div': self.depth+=1
            if tag=='span' and attrs.get('data-card'): self.current['cards'].append(attrs['data-card'])
    def handle_endtag(self, tag):
        if self.current is not None and tag=='div':
            self.depth-=1
            if self.depth==0:
                self.groups.append(self.current); self.current=None
'''
if "class BestFiveGroups" not in test_text:
    test_text = replace_once(test_text, "\ndef five(cards):", parser_code + "\n\ndef five(cards):", "best-five parser insertion")

function_pattern = re.compile(
    r"    def test_four_showdown_answers_are_independently_correct\(self\):\n.*?(?=\n    def test_full_hand_bookkeeping_matches_published_totals)",
    re.S,
)
function_replacement = '''    def test_four_showdown_answers_are_independently_correct(self):
        text=self.outputs[Path('poker/hand-rankings/index.html')]
        cases=[a for _,a in Tags(text).items if 'data-winner' in a]
        groups=BestFiveGroups(text).groups
        self.assertEqual(len(cases),4)
        self.assertEqual(len(groups),8)
        self.assertEqual(text.count('class="viewer-board-grid viewer-best-five"'),4)
        group_index=0
        for a in cases:
            first=a['data-a'].split(); second=a['data-b'].split(); board=a['data-board'].split()
            self.assertEqual(len(set(first+second+board)),9)
            one,two=best(first+board),best(second+board)
            winner='a' if one>two else 'b' if two>one else 'tie'
            self.assertEqual(winner,a['data-winner'])
            for player,hole in [('a',first),('b',second)]:
                group=groups[group_index]; group_index+=1
                declared=group['declared'].split()
                self.assertEqual(group['player'],player)
                self.assertEqual(group['cards'],declared)
                self.assertEqual(len(declared),5)
                self.assertEqual(len(set(declared)),5)
                self.assertTrue(set(declared).issubset(set(hole+board)))
                self.assertEqual(five(declared),best(hole+board))
        names=[a for _,a in Tags(text).items if a.get('role')=='img']
        self.assertEqual(len(names),126)
        self.assertTrue(all(' of ' in a.get('aria-label','') for a in names))
'''
test_text, count = function_pattern.subn(function_replacement, test_text, count=1)
if count != 1:
    raise RuntimeError(f"Expected one showdown test, found {count}")
test_path.write_text(test_text, encoding="utf-8")


browser_path = ROOT / "_tests/poker_browser.py"
browser = browser_path.read_text(encoding="utf-8")
browser = replace_once(
    browser,
    "               '/poker/episodes/test-episode/','/poker/hands/test-hand/','/poker/stories/test-story/']",
    "               '/poker/episodes/test-episode/','/poker/hands/test-hand/','/poker/stories/test-story/','/poker/hand-rankings/']",
    "poker browser route list",
)
probe = '''                page.goto(base+'/poker/hand-rankings/')
                page.locator('.viewer-question').evaluate_all('(items)=>items.forEach(x=>x.open=true)')
                expect(page.locator('.viewer-best-five-group')).to_have_count(8)
                for group in page.locator('.viewer-best-five-group').all():
                    expect(group.locator('.viewer-card[data-card]')).to_have_count(5)
                    assert group.evaluate("e=>e.dataset.bestCards===Array.from(e.querySelectorAll('[data-card]')).map(x=>x.dataset.card).join(' ')")
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
'''
if "viewer-best-five-group" not in browser:
    anchor = "                page.goto(base+'/poker/')\n                feature=page.locator('#featured-work .reader-feature-link')\n"
    browser = replace_once(browser, anchor, probe + anchor, "best-five browser probe")
browser = replace_once(
    browser,
    "PASS: 35 populated-poker route/viewport checks; expanded disclosures, text-spacing, chapter URLs, real-work feature, guide return links, escaped text, keyboard spoilers, 2 exact downloads, and no video requests.",
    "PASS: 40 populated-poker route/viewport checks; expanded disclosures, 8 best-five groups, text-spacing, chapter URLs, real-work feature, guide return links, escaped text, keyboard spoilers, 2 exact downloads, and no video requests.",
    "poker browser receipt",
)
browser_path.write_text(browser, encoding="utf-8")


report = '''# Turn 22 independent engineering pass: visible best-five showdowns

Prepared October 25, 2026, Pacific/Honolulu. This follows the printable workflow comparison release with a bounded usability improvement to the existing hand-ranking guide. The separate consenting-visitor study remains open. Automated checks do not establish visitor demand or participant outcomes.

## Reproduced gap

The four fictional showdown answers named each resulting rank string, but readers still had to translate that string back to the physical cards. This was most demanding in the shared-board tie, the competing full houses and the ace-low straight example.

## Change

Each existing answer disclosure now includes two labeled five-card groups, one for each player, before the unchanged explanation. The cards reuse the site's native responsive card components and remain hidden until the reader opens the answer. No script, remote request, storage, form, strategy recommendation or personal claim was added.

The eight selected hands are:

- Kicker: A uses Qs Qd As 9h 7c; B uses Qh Qd Jh 9h 7c.
- Shared board: both use Ah Ad Kc Kd Qs.
- Full houses: A uses As Ah Ad Kc Kd; B uses Ks Kc Kd Ah Ad.
- Ace low: A uses As 2d 3s 4h 5d; B uses 3s 4h 5d 6c 7c.

## Verification design

The unit test independently evaluates each declared five-card group, confirms that it contains five distinct available cards, and verifies that its score equals the best score available from the player's seven cards. It also confirms that the visible card elements exactly match the declared card codes. The browser suite adds the guide to all five viewport and enlarged-spacing passes, opens the four native disclosures, verifies eight groups with five cards each, and checks horizontal overflow and accessibility with the existing poker suite.

The focused authoring workflow runs the site build, HTML validation, search validation, the viewer-guide unit suite and whitespace checks before committing generated output. Full hosted release checks and automated review remain merge gates.
'''
report_path = ROOT / "_reports/website-growth/turn-22-hand-ranking-best-five.md"
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(report, encoding="utf-8")
