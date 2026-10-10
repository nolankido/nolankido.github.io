"""Curated Living Well library: static collections, access notes, and stable links."""
from __future__ import annotations
from datetime import date
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

PREFIX = '/living-well/'
ACCESS = {
    'web': 'Free to browse', 'app': 'Free core app',
    'account': 'Free account for participation', 'library': 'Library card required',
    'interactive': 'Free browser interactive',
}
TOPIC_SHELVES = {'meaning': ['meaning', 'traditions'], 'attention': ['attention', 'world', 'books-creativity'],
                'everyday-ai': ['everyday-ai', 'learning', 'digital-life', 'everyday-tools'],
                'relationships': ['care', 'contribution'], 'choices': ['thinking', 'learning']}


def safe_url(value: str) -> str:
    if not isinstance(value, str) or any(c.isspace() or ord(c) < 32 for c in value) or '\\' in value:
        raise ValueError('Resource URLs must be whitespace-free HTTPS strings')
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Resource URLs require HTTPS without credentials')
    return value


def slug(value: str) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value))


def load(root: Path) -> dict:
    data = json.loads((root / '_source/living-well/resources.json').read_text(encoding='utf-8'))
    if data.get('version') != 1:
        raise ValueError('Unknown Living Well resource catalog version')
    reviewed_on = date.fromisoformat(data['reviewed_on'])
    shelf_ids = [s['id'] for s in data['shelves']]
    if any(not slug(i) for i in shelf_ids) or len(shelf_ids) != len(set(shelf_ids)):
        raise ValueError('Invalid or duplicate Living Well shelf')
    groups = data.get('groups', [])
    group_ids = [g['id'] for g in groups]
    if not group_ids or any(not slug(i) for i in group_ids) or len(group_ids) != len(set(group_ids)):
        raise ValueError('Invalid library groups')
    for group in groups:
        if not isinstance(group.get('title'), str) or not group['title'].strip():
            raise ValueError('Library groups require a title')
    seen, destinations = set(), set()
    for entry in data['resources']:
        ident = entry['id']
        if not slug(ident) or ident in seen:
            raise ValueError('Invalid or duplicate resource ID')
        seen.add(ident)
        if entry['shelf'] not in shelf_ids or entry['access'] not in ACCESS:
            raise ValueError('Unknown resource shelf or access type')
        if entry['status'] != 'published-selection':
            raise ValueError('Unreviewed resource in public catalog')
        for field in ('title', 'creator', 'entry_title', 'requirements', 'format', 'why', 'start', 'limit', 'review_scope', 'perspective'):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                raise ValueError('Missing resource editorial field: ' + field)
        for field in ('url', 'entry_url', 'verification_url'):
            safe_url(entry[field])
        normalized = entry['entry_url'].rstrip('/')
        if normalized in destinations:
            raise ValueError('Duplicate resource starting point')
        destinations.add(normalized)
        if not slug(entry['companion']):
            raise ValueError('Invalid companion route')
        if date.fromisoformat(entry['reviewed_on']) > reviewed_on:
            raise ValueError('Resource review exceeds collection date')
    for shelf in data['shelves']:
        matches = [e for e in data['resources'] if e['shelf'] == shelf['id']]
        if not matches or shelf['start_id'] not in {e['id'] for e in matches}:
            raise ValueError('Every shelf needs a valid first selection')
        if shelf.get('group') not in group_ids or shelf.get('topic') not in TOPIC_SHELVES:
            raise ValueError('Invalid shelf grouping or topic')
        for field in ('title', 'intro', 'orientation', 'approach'):
            if not isinstance(shelf.get(field), str) or not shelf[field].strip():
                raise ValueError('Missing collection context: ' + field)
        if not isinstance(shelf.get('companions'), list) or len(shelf['companions']) != 2 or any(not slug(i) for i in shelf['companions']):
            raise ValueError('Collections need two valid companion readings')
    if any(not any(s['group'] == g for s in data['shelves']) for g in group_ids):
        raise ValueError('Empty library group')
    return data


def collection_route(ident: str) -> str:
    if not slug(ident):
        raise ValueError('Invalid collection route')
    return PREFIX + 'free-resources/' + ident + '/'


def manifest(root: Path) -> list[dict]:
    data = load(root)
    return [{'id': 'living-well-resources-' + s['id'], 'path': collection_route(s['id']),
             'title': s['title'], 'seo_title': s['title'] + ' | Living Well',
             'description': s['intro'], 'kicker': 'Living Well / Free resources',
             'source': 'living-well/page.html', 'section': 'living-well',
             'living_well_collection': s['id'], 'updated': data['reviewed_on']}
            for s in data['shelves']]


def external(url: str, label: str) -> str:
    return '<a href="' + escape(safe_url(url), quote=True) + '">' + escape(label) + '</a>'


def resource_card(entry: dict, compact: bool = False) -> str:
    e = lambda field: escape(entry[field], quote=True)
    label = escape(ACCESS[entry['access']])
    if compact:
        return ('<article class="lw-card lw-resource-preview"><p class="lw-eyebrow">' + e('format')
                + '</p><h3><a href="' + collection_route(entry['shelf']) + '#' + e('id') + '">' + e('title')
                + '</a></h3><p>' + e('why') + '</p><p class="lw-access">' + label + '</p></article>')
    return ('<article class="lw-card lw-resource" id="' + e('id') + '"><p class="lw-eyebrow">'
            + e('format') + ' · ' + label + '</p><h3>' + e('title') + '</h3>'
            + '<p class="lw-creator">' + e('creator') + '</p><p>' + e('why') + '</p>'
            + '<p><strong>Begin here:</strong> ' + e('start') + '</p>'
            + '<p class="lw-access"><strong>Access:</strong> ' + e('requirements') + '</p>'
            + '<p class="small-copy"><strong>Perspective:</strong> ' + e('perspective') + '</p>'
            + '<p>' + external(entry['entry_url'], entry['entry_title']) + '</p>'
            + '<details class="lw-resource-notes"><summary>Context &amp; source</summary><p>' + e('limit') + '</p>'
            + '<p><a href="/living-well/' + e('companion') + '/">Related reading on Living Well</a></p>'
            + '<p class="small-copy">Source information reviewed <time datetime="' + e('reviewed_on') + '">'
            + e('reviewed_on') + '</time>. ' + external(entry['verification_url'], 'Provider details')
            + '.</p><p class="small-copy">' + e('review_scope') + '</p></details></article>')


def collection_tiles(data: dict, ids: list[str] | None = None) -> str:
    shelves = [s for s in data['shelves'] if ids is None or s['id'] in ids]
    return '<div class="lw-cards lw-collection-grid">' + ''.join(
        '<article class="lw-card"><p class="lw-eyebrow">' + str(sum(e['shelf'] == s['id'] for e in data['resources']))
        + ' selected resources</p><h3><a href="' + collection_route(s['id']) + '">' + escape(s['title'])
        + '</a></h3><p>' + escape(s['intro']) + '</p></article>' for s in shelves) + '</div>'


def directory_entry(entry: dict) -> str:
    """Keep earlier #resource links usable without repeating every full annotation."""
    return ('<article class="lw-directory-entry lw-resource" id="' + escape(entry['id']) + '">'
            + '<h3>' + external(entry['entry_url'], entry['title']) + '</h3><p>' + escape(entry['why']) + '</p>'
            + '<p class="small-copy">' + escape(ACCESS[entry['access']]) + ' · ' + escape(entry['format']) + '</p>'
            + '<p class="lw-directory-detail"><a href="' + collection_route(entry['shelf']) + '#' + escape(entry['id'])
            + '">Access, context &amp; starting point for ' + escape(entry['title']) + '</a></p></article>')


def selection_notes() -> str:
    return ('<div class="prose"><p>Selections are chosen for a clear purpose, useful free material, identifiable creators, '
            'and a connection to the questions explored in Living Well. A collection should help you choose, not require '
            'you to work through everything.</p><p><strong>Different perspectives stay visible.</strong> A spiritual teaching, '
            'a philosophical argument, scientific research, and a provider’s product instructions do different jobs. '
            'Inclusion is an invitation to explore, not a claim of affiliation, personal use, or agreement with every view.</p>'
            '<p><strong>Free access has conditions.</strong> Apps can require installation, participation can require a free '
            'account, and library borrowing depends on eligibility. Optional services, printed materials, equipment, and '
            'some extra features may cost money. Access notes identify the free portion rather than describing an entire '
            'provider as free.</p><p>Source and access descriptions were reviewed on October 9, 2026. Apps have not been installed, '
            'courses have not been completed, and every media player or regional access route has not been tested. '
            'These selections are not clinical recommendations or third-party security audits. External sites manage '
            'their own privacy and accessibility.</p><p>The annotations are original and the linked material remains with '
            'its creators. There are no affiliate links or paid placements in this library. Check item-specific permissions '
            'before reusing text, images, or audio.</p><p><a href="/living-well/editorial-standards/">Editorial standards</a> · '
            '<a href="/living-well/sources/">Sources behind the articles</a> · <a href="/contact/">Send a correction</a></p></div>')


def render(root: Path, section) -> str:
    data = load(root)
    count = len(data['resources'])
    jumps = '<nav class="lw-shelf-jumps" aria-label="Free resource collections">' + ''.join(
        '<a href="#shelf-' + escape(s['id']) + '">' + escape(s['title']) + '</a>' for s in data['shelves']) + '</nav>'
    body = section('choose-one', 'The free resource library', 'Follow a useful curiosity.',
        '<p class="lw-lead">' + str(count) + ' selected resources across ' + str(len(data['shelves'])) + ' collections.</p>'
        '<p class="section-deck">Explore meaning, learn a skill, make something, or find a practical way to help. '
        'Each collection offers a manageable starting point and explains the access requirements before you go.</p>'
        '<p>Everything on Living Well is free to read and needs no account. The resources below include free public '
        'material, free core apps, and opportunities with clearly described registration or eligibility requirements.</p>'
        '<p><a href="#browse-collections">Choose a collection</a> · <a href="#resource-index">Browse the complete index</a> · '
        '<a href="#about-this-collection">How resources are selected</a></p>')
    body += section('without-signing-up', 'Only choosing one?', 'A small beginning is enough.',
        '<div class="lw-situations"><p><span>Hear a thoughtful conversation</span><a href="#on-being">An On Being conversation</a></p>'
        '<p><span>Find a free book</span><a href="#project-gutenberg">Read with Project Gutenberg</a></p>'
        '<p><span>Learn one everyday skill</span><a href="#learnfree">Start with a plain tutorial</a></p>'
        '<p><span>Explore a spiritual question in context</span><a href="' + collection_route('traditions') + '">Wisdom traditions &amp; religious literacy</a></p></div>')
    body += section('browse-collections', 'Choose a direction', 'Twelve collections, at your pace.',
        ''.join('<div class="lw-library-group"><h3>' + escape(g['title']) + '</h3>'
                + collection_tiles(data, [s['id'] for s in data['shelves'] if s['group'] == g['id']]) + '</div>' for g in data['groups']))
    body += section('resource-index', 'Complete index', 'All the starting points.',
        '<p class="section-deck">Use a collection page for fuller guidance, or follow a link here. Access and context notes '
        'remain one step away. The index also preserves links from earlier Living Well articles.</p>' + jumps)
    for shelf in data['shelves']:
        body += section('shelf-' + shelf['id'], 'Resource index', escape(shelf['title']),
            '<p class="small-copy"><a href="' + collection_route(shelf['id']) + '">Open the ' + escape(shelf['title'])
            + ' collection for access notes and suggestions</a>.</p><div class="lw-directory">'
            + ''.join(directory_entry(e) for e in data['resources'] if e['shelf'] == shelf['id'])
            + '</div><p class="lw-back"><a href="#browse-collections">Back to collection choices</a></p>')
    body += section('about-this-collection', 'Selection principles', 'Curiosity, care &amp; useful context.', selection_notes())
    return body


def detail(root: Path, ident: str, section) -> str:
    data = load(root)
    shelf = next(s for s in data['shelves'] if s['id'] == ident)
    entries = [e for e in data['resources'] if e['shelf'] == ident]
    first = next(e for e in entries if e['id'] == shelf['start_id'])
    body = section('begin', 'A useful way in', 'Choose one place to begin.',
        '<p class="section-deck">' + escape(shelf['intro']) + '</p><p class="lw-intro">' + escape(shelf['orientation'])
        + '</p><p><strong>Start with:</strong> <a href="#' + escape(first['id']) + '">' + escape(first['title'])
        + '</a>. ' + escape(first['start']) + '</p>'
        + '<nav class="lw-shelf-jumps" aria-label="Resources in this collection">' + ''.join(
            '<a href="#' + escape(e['id']) + '">' + escape(e['title']) + '</a>' for e in entries) + '</nav>')
    body += section('selected-resources', str(len(entries)) + ' selections', 'Resources with a clear purpose.',
        '<div class="lw-cards lw-resource-grid">' + ''.join(resource_card(e) for e in entries) + '</div>')
    body += section('how-to-explore', 'Keep the context', 'Take what is useful, thoughtfully.',
        '<p class="section-deck">' + escape(shelf['approach']) + '</p><p class="small-copy">Selections are based on public '
        'source review, not a claim that Nolan uses every resource or belongs to the organizations listed.</p>'
        '<p><a href="/living-well/free-resources/#about-this-collection">Selection principles and review limits</a></p>')
    # Resolve titles from the approved article catalog without importing the renderer.
    titles = {}
    for name in ('launch.json', 'further.json', 'discovery.json', 'expansion.json'):
        titles.update({e['slug']: e['title'] for e in json.loads((root / '_source/living-well' / name).read_text())['entries']})
    body += section('continue-reading', 'Related reading', 'Connect the resource to an idea.',
        '<div class="lw-situations">' + ''.join('<p><span>On Living Well</span><a href="/living-well/' + slug + '/">'
            + escape(titles[slug]) + '</a></p>' for slug in shelf['companions']) + '</div>'
        + '<p><a href="/living-well/free-resources/">All 12 resource collections</a> · '
        '<a href="/living-well/topics/' + shelf['topic'] + '/">Explore the related subject</a></p>')
    if ident in {'everyday-tools', 'everyday-ai', 'digital-life', 'care'}:
        body += section('put-a-resource-to-use', 'From reading to doing', 'Use a resource for a real task.',
            '<p class="section-deck">An app or article is a starting point. Choose a concrete result, keep the simplest adequate method, and check what actually worked.</p>'
            '<p><a href="/living-well/technology-for-real-life/">Technology for real life: seven worked guides</a></p>')
    return body


def home(root: Path, entries: list[dict], section, cards, topic_cards) -> str:
    by_slug = {e['slug']: e for e in entries}
    resources = {e['id']: e for e in load(root)['resources']}
    body = section('a-life-worth-attending-to', 'The intersection', 'More room for living.',
        '<p class="lw-lead">Spirituality, practical wisdom, and technology for everyday life.</p>'
        '<p class="section-deck">I’m interested in what makes ordinary life feel meaningful, how we become more attentive '
        'to the people and world around us, and whether technology can genuinely help.</p>'
        '<p class="lw-intro">Living Well brings those questions together through essays, selected free resources, '
        'and practical ideas. You do not need a particular belief system, an AI subscription, or a self-improvement '
        'project to begin. Start with something that interests you, and leave the rest for another time.</p>'
        '<div class="lw-primary-links"><a href="/living-well/what-i-mean-by-living-well/">Start here</a>'
        '<a href="/living-well/free-resources/">Explore free resources</a></div>')
    body += section('technology-in-ordinary-life', 'Technology for real life', 'Make one part of life easier.',
        '<p class="section-deck">Go from an interesting tool to something you can use. These worked guides show the input, a simple method, and a finish you can check.</p>'
        + cards([by_slug[s] for s in ['scattered-notes-to-next-step', 'shared-plan-people-can-use', 'find-the-document-you-need']])
        + '<p><a href="/living-well/technology-for-real-life/">Explore all seven practical guides</a> · '
        '<a href="/living-well/did-the-tool-actually-help/">Decide whether a tool helped</a></p>')
    body += section('start-where-you-are', 'Questions to explore', 'Start with a question.',
        '<div class="lw-situations"><p><span>Can something matter before you can explain it?</span>'
        '<a href="/living-well/spiritual-curiosity-reading-path/">Explore spiritual curiosity</a></p>'
        '<p><span>When does technology give us more room to live?</span>'
        '<a href="/living-well/technology-that-helps-you-notice/">A tool that helps you notice more</a></p>'
        '<p><span>Can you grow without treating yourself as a problem?</span>'
        '<a href="/living-well/growth-without-self-rejection/">Improvement without self-rejection</a></p></div>')
    body += section('three-free-starts', 'Read · try · explore', 'A few worthwhile places to go.',
        '<div class="lw-cards lw-three">' + ''.join(resource_card(resources[i], True) for i in ['on-being','ucla-mindful','seek'])
        + '</div><p><a href="/living-well/free-resources/">Browse all 66 free resources across 12 collections</a></p>')
    body += section('choose-a-route', 'Read or try', 'A short read. A place to begin.',
        '<div class="lw-routes lw-two"><article class="lw-route"><p class="lw-eyebrow">Explore an idea</p>'
        '<h3><a href="/living-well/ideas/">Essays &amp; reading paths</a></h3><p>Meaning, attention, and questions that '
        'do not need a quick answer.</p></article><article class="lw-route"><p class="lw-eyebrow">Try something</p>'
        '<h3><a href="/living-well/guides/">Practical guides</a></h3><p>Small examples, tools, and optional exercises '
        'for an ordinary day.</p></article></div>'
        + '<span id="first-collection"></span>' + cards([by_slug['read-a-poem-without-a-lesson'], by_slug['meditation-without-buying-a-lifestyle']])
        + '<p><a href="/living-well/consciousness-which-question/">Explore consciousness</a> · '
        '<a href="/living-well/learning-with-ai-without-skipping-understanding/">Try a worked AI-learning example</a></p>')
    body += section('resource-subsections', 'Explore further', 'More ways into Living Well.', collection_tiles(load(root), ['traditions', 'learning', 'books-creativity', 'digital-life', 'everyday-tools', 'contribution']))
    body += section('five-subjects', 'Browse by subject', 'Follow what interests you.', topic_cards())
    body += section('a-small-invitation', 'Keep exploring', 'No program to keep up with.',
        '<p class="section-deck">Read, listen, try something, or close the page and take the question with you. '
        'There is nothing to submit and no streak to maintain.</p><div class="link-row">'
        '<a href="/living-well/worksheets/">Private-use worksheets</a><a href="/living-well/conversations/">'
        'A conversation worth having</a><a href="/living-well/field-notes/">Proposed experiments</a></div>'
        '<p class="small-copy"><a href="/living-well/editorial-standards/">Editorial standards and AI assistance</a> · '
        '<a href="/living-well/feed.xml">Living Well RSS</a>. Personal field notes will identify the observations behind them.</p>')
    return body


def related_shelf(topic: str) -> str:
    return '<p>Explore related collections: ' + ' · '.join(
        '<a href="' + collection_route(s) + '">' + escape({
            'meaning':'Meaning and wonder', 'traditions':'Wisdom traditions', 'attention':'Attention and presence',
            'world':'Nature and science', 'books-creativity':'Books and creativity', 'everyday-ai':'AI literacy',
            'learning':'Free learning', 'digital-life':'Digital privacy', 'everyday-tools':'Useful tools',
            'care':'Relationships and memory', 'contribution':'Community contribution', 'thinking':'Philosophy and decisions'
        }[s]) + '</a>' for s in TOPIC_SHELVES[topic]) + '</p>'
