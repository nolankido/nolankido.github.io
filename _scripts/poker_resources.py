"""Reviewed external Poker links. Deterministic rendering; no network or auto-publishing."""
from __future__ import annotations
import argparse
from datetime import date, datetime, timedelta, timezone
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import parse_qsl, urlsplit, urlunsplit

# Category, local starting guide, and proposed manual review interval in days.
CATEGORIES = {
    'basics': ('Learn the basics', '/poker/start-here/', 90),
    'rules': ('Rules and procedures', '/poker/table-etiquette/', 30),
    'strategy': ('Strategy libraries and books', '/poker/ranges-and-bets/', 60),
    'math': ('Poker math and ranges', '/poker/poker-math/', 90),
    'tournament-study': ('Tournament study and ICM', '/poker/tournament-equity/', 60),
    'tools': ('Study tools and documentation', '/poker/study/', 30),
    'events': ('Official events and schedules', '/poker/tournaments/', 14),
    'results': ('Results and reporting', '/poker/variance-and-results/', 30),
    'watch-listen': ('Watch and listen', '/poker/hand-to-vlog/', 30),
    'community': ('Communities and home games', '/poker/table-etiquette/', 30),
    'variants': ('Omaha and other variants', '/poker/hand-rankings/', 90),
    'research': ('Research and development', '/poker/short-stack-decisions/', 90),
    'mental-game': ('Mental game and support', '/poker/variance-and-results/', 30),
}
ACCESS = {'Free', 'Mixed', 'Paid'}
LEVELS = {'Beginner', 'Intermediate', 'Advanced', 'Technical', 'All levels'}
FIELDS = {'id', 'title', 'url', 'publisher', 'category', 'kind', 'access', 'level',
          'description', 'notes', 'reviewed_on', 'review_method'}
ROOT = Path(__file__).resolve().parents[1]


def checked_date(value: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Resource review dates must use YYYY-MM-DD')
    return date.fromisoformat(value)


def canonical_url(value: str) -> str:
    """Compare targets without fragments, www aliases or a trailing slash."""
    if not isinstance(value, str) or any(c.isspace() or ord(c) < 32 for c in value):
        raise ValueError('Resource URL must be nonempty HTTPS text without whitespace')
    parsed = urlsplit(value)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.port not in (None, 443) or '\\' in value):
        raise ValueError('Use direct public HTTPS resource URLs without credentials')
    host = parsed.hostname.lower().removeprefix('www.')
    if '.' not in host or host in {'nolankido.com', 'localhost'}:
        raise ValueError('The external directory requires an external public hostname')
    if not re.fullmatch(r'[a-z0-9.-]+', host) or re.fullmatch(r'[0-9.]+', host):
        raise ValueError('Use a recognizable public resource domain, not an IP address')
    for key, _ in parse_qsl(parsed.query):
        if key.lower().startswith('utm_') or key.lower() in {'ref', 'affiliate', 'aff', 'affid', 'tag', 'gclid', 'fbclid', 'mc_cid', 'mc_eid'}:
            raise ValueError('Remove referral and tracking parameters from resource links')
    return urlunsplit(('https', host, parsed.path.rstrip('/'), parsed.query, ''))


def load(root: Path, *, as_of: date | None = None) -> list[dict]:
    if as_of is None:
        as_of = datetime.now(timezone.utc).date()
    if type(as_of) is not date:
        raise TypeError('as_of must be a date')
    data = json.loads((root / '_source/poker/resources.json').read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'version', 'entries'} or type(data['version']) is not int or data['version'] != 1:
        raise ValueError('Invalid external resource catalogue version')
    if not isinstance(data['entries'], list) or not data['entries']:
        raise ValueError('The resource directory needs a nonempty reviewed list')
    seen_ids, seen_urls = set(), set()
    for entry in data['entries']:
        if not isinstance(entry, dict) or set(entry) != FIELDS:
            raise ValueError('Invalid resource fields; keep candidates in the separate backlog')
        for key, value in entry.items():
            if not isinstance(value, str) or (key != 'notes' and not value.strip()):
                raise ValueError('Resource fields must be strings; only notes can be empty')
            if any(ord(c) < 32 for c in value) or chr(0x2014) in value:
                raise ValueError('Unsupported resource punctuation or control character')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', entry['id']) or entry['id'] in seen_ids:
            raise ValueError('Resource IDs must be unique lower-case slugs')
        if len(entry['title']) > 140 or len(entry['description']) > 400 or len(entry['notes']) > 400:
            raise ValueError('Keep resource titles, descriptions and notes concise')
        url = canonical_url(entry['url'])
        if url in seen_urls:
            raise ValueError('Duplicate resource destination: ' + entry['url'])
        if entry['category'] not in CATEGORIES or entry['access'] not in ACCESS or entry['level'] not in LEVELS:
            raise ValueError('Unknown resource category, access label, or audience')
        if entry['review_method'] not in {'page', 'index'}:
            raise ValueError('Resource review method must distinguish page reading from index confirmation')
        if entry['review_method'] == 'index' and not entry['notes']:
            raise ValueError('Index-only verification requires a visible limitation')
        reviewed = checked_date(entry['reviewed_on'])
        if reviewed > as_of:
            raise ValueError('Cannot claim a future resource review')
        seen_ids.add(entry['id']); seen_urls.add(url)
    return data['entries']


# The detailed publisher format remains visible. These broader buckets are for finding it.
FORMATS = {
    'reading': ('Articles and guides', {'Reference', 'Guide collection', 'Article collection', 'Article',
        'Reference collection', 'Teaching material', 'Creator essay', 'Creator archive', 'Hand analysis',
        'Lesson collection', 'Historical reference', 'Historical essay', 'Planning reference'}),
    'watch': ('Videos and courses', {'Video library', 'Video course', 'Video archive', 'Video companion',
        'Open course', 'Training library'}),
    'listen': ('Podcasts', {'Podcast', 'Podcast archive'}),
    'tools': ('Tools and documentation', {'Software', 'Calculator', 'Chart', 'Documentation', 'Specification'}),
    'official': ('Rules, events and results', {'Official rules', 'Official schedule',
        'Official event information', 'Official reporting', 'Reporting', 'Database', 'Regional directory'}),
    'community': ('Communities and support', {'Forum', 'Support information', 'Support resource'}),
    'books-research': ('Books, papers and data', {'Book information', 'Book catalogue', 'Research paper',
        'Research preprint', 'Dataset', 'Open-source repository'}),
}
TOPIC_HELP = {
    'basics': 'Start here for hand rankings, the betting sequence and unfamiliar poker terms.',
    'rules': 'Check the governing rules first. House and event-specific rulings take precedence over general explainers.',
    'strategy': 'Compare teaching perspectives. A free article library is different from a paid training subscription.',
    'math': 'Understand the calculation before using its answer: pot odds, effective stacks, combinations and equity.',
    'tournament-study': 'Match the format and model to the hand: regular tournaments, satellites and bounties are not interchangeable.',
    'tools': 'Separate free documentation from the product it describes. Study after play; a listing is not an accuracy audit.',
    'events': 'Use the organizer for dates, structures and registration. Recheck the individual event before making plans.',
    'results': 'Find coverage and recorded finishes. Tournament cashes are not a record of net profit.',
    'watch-listen': 'Choose video, audio or written creator commentary. A companion article is not a verified complete video archive.',
    'community': 'Ask questions, compare experiences or plan a home game. Forum advice is not an official ruling.',
    'variants': 'Read the rules for the exact game first, especially hole-card requirements and high-low hand selection.',
    'research': 'Technical material for examining methods, code and data. A paper or repository is not a tested poker product.',
    'mental-game': 'Distinguish performance study from help with gambling harm. Support does not require another study session.',
}


def resource_format(entry: dict) -> str:
    matches = [key for key, (_, kinds) in FORMATS.items() if entry['kind'] in kinds]
    if len(matches) != 1:
        raise ValueError('Resource format needs exactly one explicit discovery bucket: ' + entry['kind'])
    return matches[0]


def card(entry: dict) -> str:
    metadata = ' · '.join([entry['kind'], entry['access'], entry['level']])
    method = 'Page read' if entry['review_method'] == 'page' else 'Search index only'
    domain = urlsplit(entry['url']).hostname.removeprefix('www.')
    return (f'<article class="reader-card" id="resource-{entry["id"]}" data-resource-card tabindex="-1" '
            f'data-category="{entry["category"]}" data-access="{entry["access"]}" '
            f'data-level="{entry["level"]}" data-format="{resource_format(entry)}">'
            f'<p class="reader-eyebrow">{escape(entry["publisher"])} <span class="resource-domain">{escape(domain)}</span></p>'
            f'<h3><a href="{escape(entry["url"], quote=True)}" rel="external">{escape(entry["title"])}</a></h3>'
            f'<p class="reader-card-meta">{escape(metadata)}</p>'
            f'<p class="resource-description">{escape(entry["description"])}</p>'
            + (f'<p class="small-copy resource-caution"><strong>Before you use it:</strong> {escape(entry["notes"])}</p>' if entry['notes'] else '')
            + f'<p class="small-copy resource-review">Listing reviewed <time datetime="{entry["reviewed_on"]}">{entry["reviewed_on"]}</time>'
            f' · <a href="#review-policy">{method}</a>'
            f' · <a href="#resource-{entry["id"]}" data-resource-jump aria-label="Link to listing: {escape(entry["title"], quote=True)}">Link to listing</a></p></article>')


# Editorial starting points use existing IDs, not a second resource catalogue.
STARTING_PATHS = (
    ('Learn the game', 'Start with the deal, check hand rankings, then work through a lesson.',
     ('holdem-rules', 'hand-rankings', 'pokerology-lessons')),
    ('Review a tournament decision', 'Check the call price, prize-equity model, and format before a verdict.',
     ('pot-odds', 'icm-basics', 'satellite-guide')),
    ('Compare cash-game and Omaha study', 'Choose the exact game you play. These are separate starting points, not one transferable set of ranges.',
     ('splitsuit', 'plo-mastermind-blog', 'equity-realization')),
    ('Watch the thinking behind a hand', 'Use a creator account and a separate hand breakdown, not results alone.',
     ('brad-owen-wpt-vlog', 'jaman-hand-breakdown', 'lexy-vlog-notes')),
    ('Find official event information', 'Start with the organizer, then check the specific schedule and structure.',
     ('wsop-schedule', 'thunder-valley-poker', 'wynn-poker')),
    ('Inspect tools and data', 'Read the manual, record format, or implementation before relying on outputs.',
     ('pio-quick-start', 'phh-format', 'treys-evaluator')),
)


def starting_paths(entries: list[dict], paths=STARTING_PATHS) -> str:
    by_id = {entry['id']: entry for entry in entries}
    articles = []
    for title, reason, ids in paths:
        if not 2 <= len(ids) <= 4 or len(ids) != len(set(ids)) or any(ident not in by_id for ident in ids):
            raise ValueError('Starting paths need distinct IDs from the reviewed resource catalogue')
        links = ''.join(f'<li><a href="#resource-{ident}" data-resource-jump>{escape(by_id[ident]["title"])}</a>'
                        f' <span class="small-copy">({escape(by_id[ident]["access"])})</span></li>' for ident in ids)
        articles.append(f'<article><h3>{escape(title)}</h3><p>{escape(reason)}</p><ol>{links}</ol></article>')
    return ('<details class="poker-details" id="resource-starting-points"><summary>Start with a question: six reading paths</summary>'
            '<p>Editorial starting points, not rankings or required courses. Each link opens its listing below, '
            'with access, context and limits. Starting-point links clear active filters.</p>'
            '<div class="viewer-learning-paths">' + ''.join(articles) + '</div></details>')


def supplement(entries: list[dict]) -> dict[str, str]:
    counts = {category: sum(e['category'] == category for e in entries) for category in CATEGORIES}
    buttons = '<button type="button" data-resource-filter="all" aria-pressed="true">All topics</button>'
    jumps, groups = [], []
    for category, (label, guide, _) in CATEGORIES.items():
        if not counts[category]:
            continue
        buttons += (f'<button type="button" data-resource-filter="{category}" aria-pressed="false">'
                    f'{escape(label)} ({counts[category]})</button>')
        jumps.append(f'<a href="#{category}" data-resource-jump>{escape(label)} ({counts[category]})</a>')
        cards = ''.join(card(e) for e in sorted(entries, key=lambda e: e['title'].casefold()) if e['category'] == category)
        groups.append(f'<section class="section folio-row" id="{category}" data-resource-section aria-labelledby="{category}-heading">'
                      f'<div class="section-meta"><p class="section-label">Elsewhere online</p></div><div class="section-content">'
                      f'<h2 class="section-title" id="{category}-heading">{escape(label)}</h2>'
                      f'<p class="resource-topic-help">{escape(TOPIC_HELP[category])}</p>'
                      f'<p class="small-copy"><a href="{guide}">Related reading on this site</a> · <a href="#directory-top">Back to directory controls</a></p>'
                      f'<div class="reader-grid">{cards}</div></div></section>')
    formats = ''.join(f'<option value="{key}">{escape(label)}</option>' for key, (label, _) in FORMATS.items())
    levels = ''.join(f'<option value="{level}">{level}</option>' for level in ['Beginner', 'Intermediate', 'Advanced', 'Technical'])
    goals = ''.join(f'<button type="button" data-resource-goal="{goal}">{label}</button>' for goal, label in [
        ('beginner', 'New to poker + free'), ('tournament', 'Tournament study'), ('watch', 'Creators, video & audio'),
        ('tools', 'Find a study tool'), ('events', 'Find official events'), ('variants', 'Omaha and mixed games')])
    controls = ('<div class="reader-controls" id="resource-controls" hidden>'
                '<label for="resource-search">What are you looking for?</label><div class="reader-search-row">'
                '<input type="search" id="resource-search" maxlength="160" autocomplete="off" spellcheck="false" '
                'placeholder="Try ICM, Omaha, hand history or a publisher" aria-describedby="resource-search-help">'
                '<button type="button" id="resource-reset">Clear filters</button></div>'
                '<p class="reader-help" id="resource-search-help">Search titles, publishers, topics and notes. All words must match; Enter jumps to results. '
                'Nothing is sent or saved.</p>'
                '<details class="poker-details resource-refine"><summary>Refine by format, experience or topic</summary>'
                '<div class="resource-selects"><div><label for="resource-format">Resource type</label><select id="resource-format">'
                '<option value="all">Any format</option>' + formats + '</select></div>'
                '<div><label for="resource-level">Experience</label><select id="resource-level" aria-describedby="resource-level-help">'
                '<option value="all">Any experience level</option>' + levels + '</select></div></div>'
                '<p class="reader-help" id="resource-level-help">An experience filter also includes general resources marked All levels. '
                'Resource type does not guarantee captions, transcripts or account-free access.</p>'
                '<div class="reader-filters" role="group" aria-label="External resource topics">' + buttons + '</div></details>'
                '<div class="reader-filters"><button type="button" id="resource-free" aria-pressed="false">Free resources only</button>'
                '<button type="button" id="resource-compact" aria-pressed="false">Compact list</button>'
                '</div>'
                '<div class="resource-quick"><p class="reader-help"><strong>Not sure where to begin?</strong> A choice replaces filters and opens results below.</p>'
                '<div class="reader-filters" role="group" aria-label="Starting choices">' + goals + '</div></div>'
                '<p class="reader-help" id="resource-active">All topics. Any format. Any experience. Free, mixed and paid.</p></div>')
    return {'poker_resource_count': str(len(entries)), 'poker_resource_topic_count': str(sum(bool(n) for n in counts.values())),
            'poker_resource_controls': controls, 'poker_resource_paths': starting_paths(entries),
            'poker_resource_jumps': '<nav class="poker-jump" aria-label="Resource categories">' + ''.join(jumps) + '</nav>',
            'poker_resource_groups': '\n'.join(groups)}


def review_queue(entries: list[dict], as_of: date) -> list[dict]:
    """A proposed manual work queue, not a network check or a scheduled task."""
    result = []
    for entry in entries:
        due = checked_date(entry['reviewed_on']) + timedelta(days=CATEGORIES[entry['category']][2])
        if due <= as_of or entry['review_method'] == 'index':
            result.append({'id': entry['id'], 'url': entry['url'], 'due': due.isoformat(),
                           'reason': 'Needs direct page review' if entry['review_method'] == 'index' else 'Review interval reached'})
    return sorted(result, key=lambda e: (e['reason'] != 'Needs direct page review', e['due'], e['id']))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of', required=True, type=checked_date, help='Explicit date for a proposed manual review queue')
    args = parser.parse_args()
    entries = load(ROOT, as_of=args.as_of)
    print(json.dumps({'as_of': args.as_of.isoformat(), 'total': len(entries), 'network_checks_performed': False,
                      'review_queue': review_queue(entries, args.as_of)}, indent=2))


if __name__ == '__main__':
    main()
