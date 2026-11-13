"""A complete, native author archive derived from published article records."""
from copy import deepcopy
from datetime import date
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path

import local_laptop_case
import poker_episode
import poker_standoff_episode
import reply_audit_case

ASSET = Path('assets/author-archive.css')
BEGIN = '<!-- Author archive: start -->'
END = '<!-- Author archive: end -->'
GROUPS = (
    ('practical-ai', 'Practical AI', 'Checking AI work, deciding when to use it, and keeping human judgment visible.'),
    ('living-well', 'Living Well', 'Essays, practical guides and explicitly proposed experiments for ordinary life.'),
    ('poker', 'Poker', 'Explanations, worked study material and first-person video companions with their source limits.'),
    ('general-essays', 'General essays & creative work', 'Learning, decisions, explanation and finishing something worth sharing.'),
)
AI_NOTES = frozenset({'keep-the-judgment', 'trustworthy-tools'})
PERSON_ID = 'https://nolankido.com/about/#nolan-kido'
STANDALONE_LABELS = {
    'local-ai-guide': 'Practical guide',
    'reply-audit': 'Recorded case',
    'poker-companion': 'First-person video companion',
}
# These four registered Articles retain their separate builders. The player
# profile, private drafts and unregistered files are deliberately not scanned.
STANDALONE_ARTICLES = (
    ('local-ai-gaming-laptop', local_laptop_case, 'technology', 'local-ai-guide', ''),
    ('review-reply-evidence-audit', reply_audit_case, 'technology', 'reply-audit', ''),
    ('poker-portland-meadows-ep1', poker_episode, 'poker', 'poker-companion',
     'Based on archived narration; the current video’s scene timing has not been independently checked.'),
    ('poker-portland-meadows-standoff', poker_standoff_episode, 'poker', 'poker-companion',
     'Based on an archived production packet; the current video has not been independently compared with that source.'),
)


class _ArticleMetadata(HTMLParser):
    """Read the public text absent from the two older companion registries."""
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.headlines = []
        self.descriptions = []
        self.schemas = []
        self.in_heading = False
        self.in_schema = False
        self.schema_text = ''
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h1':
            self.headlines.append('')
            self.in_heading = True
        if tag == 'meta' and attrs.get('name') == 'description':
            self.descriptions.append(attrs.get('content'))
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.in_schema = True
            self.schema_text = ''

    def handle_data(self, data):
        if self.in_heading:
            self.headlines[-1] += data
        if self.in_schema:
            self.schema_text += data

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_heading = False
        if tag == 'script' and self.in_schema:
            self.schemas.append(json.loads(self.schema_text))
            self.in_schema = False


def _standalone_records(root):
    """Reuse only complete publications accepted by their existing registries."""
    rows = []
    for ident, registry, section, kind, note in STANDALONE_ARTICLES:
        item = registry.record(root)
        if item is None:
            continue
        route = item.get('path', item.get('route'))
        if route != registry.ROUTE or item.get('url') != registry.URL:
            raise ValueError('Standalone archive entry requires its registered canonical route')
        document = _ArticleMetadata((root / registry.OUTPUT).read_text(encoding='utf-8'))
        if (document.headlines != [item['title']] or len(document.descriptions) != 1
                or len(document.schemas) != 1):
            raise ValueError('Standalone archive needs one matching headline, description and Article')
        description = document.descriptions[0]
        schema = document.schemas[0]
        if (not isinstance(description, str) or not description.strip() or len(description) > 320
                or not isinstance(schema, dict) or schema.get('@type') != 'Article'
                or schema.get('url') != item['url']
                or schema.get('headline') != item['title']
                or schema.get('description') != description
                or schema.get('datePublished') != item['date']
                or not isinstance(schema.get('author'), dict)
                or schema['author'].get('@id') != PERSON_ID
                or ('description' in item and item['description'] != description)):
            raise ValueError('Standalone archive metadata must match its public Article and author')
        row = {'id': ident, 'path': route, 'title': item['title'],
               'description': description, 'date': item['date'],
               'section': section, 'archive_kind': kind}
        if note:
            row['archive_note'] = note
        rows.append(row)
    return rows


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
    if 'archive_kind' in page:
        if page['archive_kind'] not in STANDALONE_LABELS:
            raise ValueError('Unknown standalone article label')
        return STANDALONE_LABELS[page['archive_kind']]
    if page['id'] == 'accounting-research': return 'Published research explanation'
    if page.get('evidence_article'): return 'Recorded case'
    if page.get('worked_guide'): return 'Guide with worked examples'
    if page.get('living_well_kind') == 'experiment': return 'Proposed experiment'
    if page.get('living_well_kind') == 'guide': return 'Practical guide'
    if page.get('note') or page.get('living_well_kind') == 'essay': return 'AI-assisted essay'
    return 'Poker guide'


def records(pages, root=None):
    """Keep manifest-only historical fixtures; explicitly add live registries."""
    selected = [deepcopy(p) for p in pages if is_article(p)]
    if root is not None:
        standalone = _standalone_records(Path(root))
        owned_paths = {p['path'] for p in pages}
        owned_ids = {p['id'] for p in pages}
        if any(p['path'] in owned_paths or p['id'] in owned_ids for p in standalone):
            raise ValueError('Standalone archive ownership collides with the main manifest')
        selected.extend(standalone)
    if len({p['path'] for p in selected}) != len(selected):
        raise ValueError('Author archive must not duplicate canonical articles')
    if len({p['id'] for p in selected}) != len(selected):
        raise ValueError('Author archive must not duplicate article IDs')
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


def body(page, content, pages, root=None):
    if page['id'] not in {'about', 'notes'}:
        return content
    entries = records(pages, root)
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
            intro += '<li data-archive-id="' + escape(p['id'], quote=True) + '"><a href="' + escape(p['path'], quote=True) + '">' + escape(p['title']) + '</a><p class="archive-meta">' + escape(label(p)) + ' · Published <time datetime="' + p['date'] + '">' + published + '</time></p><p class="archive-description">' + escape(p['description']) + '</p>'
            if p.get('archive_note'):
                intro += '<p class="small-copy archive-source-note">' + escape(p['archive_note']) + '</p>'
            intro += '</li>'
        intro += '</ul></details>'
    intro += '<p class="small-copy">AI assistance and source or example limitations are disclosed on the articles. A proposed experiment is a plan, not a completed personal result. Tools, topic hubs and outside-resource directories remain in <a href="/resources/">Resources</a>.</p></div></section>'
    anchor = '<section class="section folio-row" id="follow"'
    if anchor not in content: raise ValueError('Author archive needs the existing Writing footer')
    return content.replace(anchor, marked(intro) + anchor, 1)


def schema(page, content, pages, site, root=None):
    if page['id'] != 'notes': return content
    result = deepcopy(content)
    entries = records(pages, root)
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
