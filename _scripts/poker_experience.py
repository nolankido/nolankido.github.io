"""Connect approved Poker work to existing reader paths, without a new catalog."""
from html import escape
from urllib.parse import urlsplit
import poker_content


def real_entries(data: dict) -> list[dict]:
    """Only loaded, approved accounts can occupy the real-work feature."""
    return sorted((e for e in data['entries']
                   if e.get('approved') is True
                   and (e['kind'] in ('episode', 'story')
                        or e.get('record_type') == 'reconstructed')),
                  key=lambda e: (e['published'], e['slug']), reverse=True)


def label(entry: dict) -> str:
    return {'episode': 'Episode companion', 'story': 'Poker story',
            'hand': 'Reconstructed hand'}[entry['kind']]


def supplement(data: dict) -> dict[str, str]:
    entries = real_entries(data)
    if not entries:
        return {'poker_feature': '', 'poker_intro_action':
                '<div class="link-row"><a class="button" href="/poker/follow-along/">'
                'Start with one hand <span aria-hidden="true">→</span></a></div>'}
    entry = entries[0]
    action = 'Watch and read' if entry['kind'] == 'episode' else 'Read the hand' if entry['kind'] == 'hand' else 'Read the story'
    feature = ('<section class="section folio-row" id="featured-work" aria-labelledby="poker-feature-title">'
               '<div class="section-meta"><p class="section-label">Featured / Watch &amp; read</p></div>'
               '<div class="section-content"><article class="reader-feature">'
               f'<p class="reader-eyebrow">{label(entry)}</p>'
               f'<h2 id="poker-feature-title">{escape(entry["title"])}</h2>'
               f'<p>{escape(entry["summary"])}</p>' + poker_content.image_html(entry) +
               f'<a class="reader-feature-link" href="{poker_content.route(entry)}">{action}'
               ' <span aria-hidden="true">→</span></a>'
               f'<p class="reader-published-note">Published <time datetime="{entry["published"]}">'
               f'{entry["published"]}</time></p></article></div></section>')
    return {'poker_feature': feature, 'poker_intro_action': ''}


def related_work(data: dict, page_path: str) -> str:
    """Return links only when an approved account explicitly cites this guide.

    Fragments can identify a precise explanation. Similar paths, other hosts,
    lookalike domains and merely related topics do not establish a connection.
    """
    matches = []
    for entry in real_entries(data):
        for source in entry.get('sources', []):
            url = urlsplit(source['url'])
            if (url.scheme == 'https'
                    and url.netloc in ('nolankido.com', 'www.nolankido.com')
                    and url.path == page_path):
                matches.append(entry)
                break
    if not matches:
        return ''
    cards = ''.join(
        '<article class="poker-content-card">'
        f'<p class="note-category">{label(entry)}</p>'
        f'<h3><a href="{poker_content.route(entry)}">{escape(entry["title"])}</a></h3>'
        f'<p>{escape(entry["summary"])}</p></article>' for entry in matches[:3])
    return ('<section class="section folio-row" aria-labelledby="context-reading-title">'
            '<div class="section-meta"><p class="section-label">Watch &amp; read</p></div>'
            '<div class="section-content"><h2 class="section-title" id="context-reading-title">'
            'See this explanation in context.</h2><p>These published accounts refer to this guide. '
            'Return to the specific hand or story, rather than starting the library again.</p>'
            f'<div class="poker-content-grid">{cards}</div></div></section>')
