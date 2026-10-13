"""A complete, native author archive derived from published article records."""
from copy import deepcopy
from datetime import date
from hashlib import sha256
from html import escape
from pathlib import Path

ASSET = Path('assets/author-archive.css')
BEGIN = '<!-- Author archive: start -->'
END = '<!-- Author archive: end -->'
GROUPS = (
    ('practical-ai', 'Practical AI', 'Checking AI work, deciding when to use it, and keeping human judgment visible.'),
    ('living-well', 'Living Well', 'Essays, practical guides and explicitly proposed experiments for ordinary life.'),
    ('poker', 'Poker', 'Explanations, worked study material and guides for decisions away from play.'),
    ('general-essays', 'General essays & creative work', 'Learning, decisions, explanation and finishing something worth sharing.'),
)
AI_NOTES = frozenset({'keep-the-judgment', 'trustworthy-tools'})


def is_article(page):
    return not page.get('noindex') and any(page.get(k) for k in
        ('note', 'poker_entry', 'poker_guide', 'living_well_entry', 'evidence_article', 'worked_guide'))


def group(page):
    if page.get('section') == 'technology' or page['id'] in AI_NOTES:
        return 'practical-ai'
    if page['path'].startswith('/living-well/'):
        return 'living-well'
    if page['path'].startswith('/poker/'):
        return 'poker'
    return 'general-essays'


def label(page):
    if page.get('evidence_article'): return 'Recorded case'
    if page.get('worked_guide'): return 'Guide with worked examples'
    if page.get('living_well_kind') == 'experiment': return 'Proposed experiment'
    if page.get('living_well_kind') == 'guide': return 'Practical guide'
    if page.get('note') or page.get('living_well_kind') == 'essay': return 'AI-assisted essay'
    return 'Poker guide'


def records(pages):
    selected = [deepcopy(p) for p in pages if is_article(p)]
    if len({p['path'] for p in selected}) != len(selected):
        raise ValueError('Author archive must not duplicate canonical articles')
    for p in selected:
        date.fromisoformat(p['date'])
        if not p['path'].startswith('/') or not p['path'].endswith('/'):
            raise ValueError('Author archive needs canonical local article routes')
    return sorted(selected, key=lambda p: (p['title'].casefold(), p['path']))


def metadata(pages):
    result = deepcopy(pages)
    for p in result:
        if p['id'] == 'about': p['updated'] = max(p.get('updated', ''), '2026-10-12')
    return result


def marked(text):
    return BEGIN + text + END


def body(page, content, pages):
    entries = records(pages)
    count = len(entries)
    if page['id'] == 'about':
        return content + marked('<section class="section"><div class="shell editorial-grid"><div class="section-meta"><p class="section-label">Writing by Nolan Kido</p></div><div class="section-content prose"><h2>A fuller view of the writing</h2><p>The <a href="/notes/#all-writing">complete writing archive</a> brings together ' + str(count) + ' published pieces across practical AI, Living Well, poker and general essays. Each entry keeps its original publication date and identifies its kind of material.</p><p>Begin with the selected reading paths, or open one subject to browse the full collection. Proposed experiments are plans to try, not reports of completed results.</p></div></div></section>')
    if page['id'] != 'notes': return content
    shortcut = marked('<p class="archive-shortcut"><a href="#all-writing">Browse all ' + str(count) + ' pieces by subject</a>, with publication dates and material labels.</p>')
    content = content.replace('<nav class="link-row" aria-label="Writing topics">', shortcut + '<nav class="link-row" aria-label="Writing topics">', 1)
    intro = '<section class="section folio-row author-archive" id="all-writing" aria-labelledby="all-writing-title"><div class="section-meta"><p class="section-label">The complete archive</p></div><div class="section-content"><h2 class="section-title" id="all-writing-title">Writing by Nolan Kido</h2><p class="section-deck">All ' + str(count) + ' published articles, grouped by subject and alphabetized within each group. Choose a subject to open its list. The short reading paths above are still the easiest way to begin.</p><p class="small-copy"><a href="/about/" rel="author">About Nolan</a> · <a href="/start-here/#reading-this-site">How to read this material</a> · <a href="/follow/">Follow future writing</a></p>'
    for key, title, description in GROUPS:
        items = [p for p in entries if group(p) == key]
        intro += '<details class="archive-group" id="archive-' + key + '"><summary>' + escape(title) + ' <span>(' + str(len(items)) + ')</span></summary><p>' + escape(description) + '</p><ul class="archive-list">'
        for p in items:
            dt = date.fromisoformat(p['date'])
            published = dt.strftime('%B') + ' ' + str(dt.day) + ', ' + str(dt.year)
            intro += '<li data-archive-id="' + escape(p['id'], quote=True) + '"><a href="' + escape(p['path'], quote=True) + '">' + escape(p['title']) + '</a><p class="archive-meta">' + escape(label(p)) + ' · Published <time datetime="' + p['date'] + '">' + published + '</time></p><p class="archive-description">' + escape(p['description']) + '</p></li>'
        intro += '</ul></details>'
    intro += '<p class="small-copy">AI assistance and source or example limitations are disclosed on the articles. A proposed experiment is a plan, not a completed personal result. Tools, topic hubs and outside-resource directories remain in <a href="/resources/">Resources</a>.</p></div></section>'
    anchor = '<section class="section folio-row" id="follow"'
    if anchor not in content: raise ValueError('Author archive needs the existing Writing footer')
    return content.replace(anchor, marked(intro) + anchor, 1)


def schema(page, content, pages, site):
    if page['id'] != 'notes': return content
    result = deepcopy(content)
    entries = records(pages)
    ordered = [p for key, _, _ in GROUPS for p in entries if group(p) == key]
    result['creator'] = {'@type': 'Person', '@id': site['url'] + '/about/#nolan-kido', 'name': site['name'], 'url': site['url'] + '/about/'}
    result['mainEntity'] = {'@type': 'ItemList', '@id': site['url'] + '/notes/#all-writing',
        'name': 'Writing by ' + site['name'], 'numberOfItems': len(ordered),
        'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': p['title'], 'url': site['url'] + p['path']} for i, p in enumerate(ordered, 1)]}
    return result


def head(page, root):
    if page['id'] != 'notes': return ''
    version = sha256((root / ASSET).read_bytes()).hexdigest()[:12]
    return '\n  <link rel="stylesheet" href="/assets/author-archive.css?v=' + version + '">'
