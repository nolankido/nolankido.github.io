"""Build-time reader navigation. No script, generated IDs, or answer spoilers.

The outline reads only existing, visible h2 anchors in the article body, before
related cards are appended. It never changes original guide text or fragments.
"""
from html import escape
from html.parser import HTMLParser
import re

NEXT_READS = {
'omaha-hi-lo-workshop': ('stud-and-lowball-workshop', 'omaha-and-mixed-games'),
'stud-and-lowball-workshop': ('omaha-hi-lo-workshop', 'poker-rules-and-fair-play'),
'multiway-pot-workshop': ('side-pot-lab', 'pot-odds-workshop'),
'poker-media-study': ('evaluating-poker-advice', 'range-combinations'),
'poker-access-and-protection': ('poker-rules-and-fair-play', 'first-live-tournament'),

    'poker-math-reference': ('pot-odds-workshop', 'flush-and-redraw'),
    'reading-preflop-charts': ('range-combinations', 'short-stack-decisions'),
    'poker-rules-and-fair-play': ('table-etiquette', 'first-live-tournament'),
    'free-poker-learning-path': ('holdem-basics', 'pot-odds-workshop'),
    'cash-game-study': ('position-and-stacks', 'side-pot-lab'),
    'omaha-and-mixed-games': ('hand-rankings', 'betting-and-pots'),
    'poker-books-and-courses': ('free-poker-learning-path', 'evaluating-poker-advice'),
    'poker-research-guide': ('choosing-study-tools', 'tournament-equity'),
    'first-live-tournament': ('choosing-a-tournament', 'tournament-day'),
    'choosing-a-tournament': ('registration-and-reentry', 'tournament-formats'),
    'registration-and-reentry': ('tournament-day', 'variance-and-results'),
    'tournament-day': ('recording-hands', 'table-etiquette'),
    'recording-hands': ('reviewing-a-hand', 'pot-odds-workshop'),
    'choosing-study-tools': ('evaluating-poker-advice', 'tournament-equity'),
    'evaluating-poker-advice': ('choosing-study-tools', 'decision-lab'),

    'decision-lab': ('range-combinations', 'pot-odds-workshop'),
    'flush-and-redraw': ('reading-the-board', 'pot-odds-workshop'),
    'side-pot-lab': ('betting-and-pots', 'short-stack-decisions'),
    'holdem-basics': ('hand-rankings', 'betting-and-pots'),
    'hand-rankings': ('reading-the-board', 'flush-and-redraw'),
    'betting-and-pots': ('side-pot-lab', 'pot-odds-workshop'),
    'glossary': ('holdem-basics', 'follow-along'),
    'viewer-questions': ('holdem-basics', 'follow-along'),
    'position-and-stacks': ('ranges-and-bets', 'short-stack-decisions'),
    'reading-the-board': ('flush-and-redraw', 'range-combinations'),
    'ranges-and-bets': ('range-combinations', 'decision-lab'),
    'poker-math': ('pot-odds-workshop', 'practice-room'),
    'pot-odds-workshop': ('decision-lab', 'flush-and-redraw'),
    'range-combinations': ('decision-lab', 'practice-room'),
    'tournaments': ('tournament-formats', 'short-stack-decisions'),
    'tournament-formats': ('tournament-equity', 'practice-room'),
    'table-etiquette': ('betting-and-pots', 'hand-to-vlog'),
    'short-stack-decisions': ('side-pot-lab', 'tournament-equity'),
    'tournament-equity': ('short-stack-decisions', 'practice-room'),
    'follow-along': ('flush-and-redraw', 'side-pot-lab'),
    'practice-room': ('decision-lab', 'side-pot-lab'),
    'reviewing-a-hand': ('pot-odds-workshop', 'hand-to-vlog'),
    'variance-and-results': ('reviewing-a-hand', 'hand-to-vlog'),
    'hand-to-vlog': ('reviewing-a-hand', 'variance-and-results'),
}

class VisibleHeadings(HTMLParser):
    """Collect named h2s, excluding details, hidden subtrees, scripts and styles."""
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.headings: list[tuple[str, str]] = []
        self.active: tuple[str, list[str]] | None = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        blocked = (bool(self.stack and self.stack[-1][1]) or tag in {'details', 'script', 'style'}
                   or 'hidden' in attrs or attrs.get('aria-hidden') == 'true')
        if tag not in self.VOID:
            self.stack.append((tag, blocked))
        if tag == 'br' and self.active:
            self.active[1].append(' ')
        if tag == 'h2':
            anchor = attrs.get('id', '')
            self.active = (anchor, []) if not blocked and re.fullmatch(r'[A-Za-z0-9_-]+', anchor) else None

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == 'h2' and self.active:
            anchor, words = self.active
            label = ' '.join(''.join(words).split())
            if label:
                self.headings.append((anchor, label))
            self.active = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.active and not (self.stack and self.stack[-1][1]):
            self.active[1].append(data)


def section_outline(source: str) -> str:
    """Skip the opening heading and render existing major-section anchors only."""
    headings = VisibleHeadings(source).headings[1:]
    if len(headings) < 2:
        return ''
    seen = set()
    links = []
    for anchor, label in headings:
        if anchor in seen:
            raise ValueError('Duplicate reading anchor: ' + anchor)
        seen.add(anchor)
        links.append(f'<li><a href="#{escape(anchor, quote=True)}">{escape(label)}</a></li>')
    return ('<details class="reader-outline"><summary>On this page '
            f'<span class="reader-outline-count">{len(links)} sections</span></summary>'
            '<nav aria-label="On this page"><ol>' + ''.join(links) + '</ol></nav></details>')


def next_reads(item: dict, entries: list[dict]) -> list[dict]:
    """Use available editorial picks, then fill missing slots without self-links."""
    by_slug = {entry['slug']: entry for entry in entries}
    result = [by_slug[slug] for slug in NEXT_READS.get(item['slug'], ())
              if slug in by_slug and slug != item['slug']]
    candidates = sorted(entries, key=lambda entry: entry['topic'] != item['topic'])
    for entry in candidates:
        if len(result) >= 2:
            break
        if entry['slug'] != item['slug'] and entry not in result:
            result.append(entry)
    return result[:2]
