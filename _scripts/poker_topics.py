"""One editorial topic map over existing guides and external resource records.

This module never downloads, duplicates, ranks or silently approves a resource.
The specialized directory sections keep their existing URLs and filters.
"""
from __future__ import annotations
from collections import Counter
from html import escape
import json
from pathlib import Path
import re
import poker_resources

FIELDS = {'id', 'title', 'summary', 'primary_guides', 'related_guides',
          'resource_categories', 'resource_ids', 'featured_resources', 'start_label',
          'steps', 'glossary_terms', 'overview_routes'}


def load(root: Path, pages: list[dict], guides: list[dict], resources: list[dict]) -> list[dict]:
    data = json.loads((root / '_source/poker/topics.json').read_text(encoding='utf-8'))
    if (not isinstance(data, dict) or set(data) != {'version', 'entries'}
            or type(data['version']) is not int or data['version'] != 1
            or not isinstance(data['entries'], list) or not data['entries']):
        raise ValueError('Invalid Poker topic map')
    by_slug = {g['slug']: g for g in guides}
    by_id = {r['id']: r for r in resources}
    page_routes = {p['path'] for p in pages}
    seen, primary, covered = set(), [], set()
    result = []
    for topic in data['entries']:
        if not isinstance(topic, dict) or set(topic) != FIELDS:
            raise ValueError('Invalid topic fields')
        for field in ('id', 'title', 'summary', 'start_label'):
            value = topic[field]
            if (not isinstance(value, str) or not value.strip()
                    or any(ord(c) < 32 for c in value)):
                raise ValueError('Topic text must be nonempty plain text')
        if not re.fullmatch(r'[a-z]+(?:-[a-z]+)*', topic['id']) or topic['id'] in seen:
            raise ValueError('Unsafe or duplicate topic ID')
        seen.add(topic['id'])
        for field in ('primary_guides', 'related_guides', 'resource_categories', 'resource_ids',
                      'featured_resources', 'glossary_terms', 'overview_routes'):
            values = topic[field]
            if (not isinstance(values, list) or not all(isinstance(v, str) for v in values)
                    or len(values) != len(set(values))):
                raise ValueError('Topic references must be distinct string lists')
        slugs = topic['primary_guides'] + topic['related_guides']
        if len(slugs) != len(set(slugs)) or any(s not in by_slug for s in slugs):
            raise ValueError('Unknown or duplicated guide within topic')
        if any(route not in page_routes for route in topic['overview_routes']):
            raise ValueError('Unknown topic overview route')
        if any(c not in poker_resources.CATEGORIES for c in topic['resource_categories']):
            raise ValueError('Unknown source directory section')
        if any(i not in by_id for i in topic['resource_ids'] + topic['featured_resources']):
            raise ValueError('Unknown topic resource ID')
        chosen = {r['id'] for r in resources if r['category'] in topic['resource_categories']} | set(topic['resource_ids'])
        if not chosen or not 2 <= len(topic['featured_resources']) <= 4 or not set(topic['featured_resources']) <= chosen:
            raise ValueError('Topic needs 2 to 4 featured sources from its membership')
        steps = topic['steps']
        if (not isinstance(steps, list) or not 2 <= len(steps) <= 3
                or any(not isinstance(s, dict) or set(s) != {'guide', 'label'} for s in steps)):
            raise ValueError('Topic needs 2 or 3 guide steps')
        for step in steps:
            if step['guide'] not in slugs or not isinstance(step['label'], str) or not step['label'].strip():
                raise ValueError('Topic step must reference a member guide with a label')
        if len({s['guide'] for s in steps}) != len(steps):
            raise ValueError('Duplicate topic step')
        primary.extend(topic['primary_guides']); covered.update(chosen)
        result.append({**topic, 'guides': [by_slug[s] for s in slugs],
                       'resources': [by_id[i] for i in sorted(chosen)],
                       'featured': [by_id[i] for i in topic['featured_resources']]})
    if Counter(primary) != Counter(by_slug.keys()):
        raise ValueError('Every published guide needs exactly one primary topic')
    if covered != set(by_id):
        raise ValueError('Every reviewed external source needs a topic')
    return result


def manifest(root: Path) -> list[dict]:
    """Focused topic pages are generated from the same editorial registry."""
    data = json.loads((root / '_source/poker/topics.json').read_text(encoding='utf-8'))
    return [{'id': 'poker-topic-' + t['id'], 'path': '/poker/topics/' + t['id'] + '/',
             'title': t['title'], 'seo_title': t['title'] + ' | Poker Resources | Nolan Kido',
             'description': t['summary'] + ' Find starting guides and selected outside sources, with access labels and review context.',
             'kicker': 'Poker / Topics', 'section': 'poker', 'source': 'poker/topic.html',
             'poker_topic': t['id'], 'updated': '2026-10-08'} for t in data['entries']]


def finder_url(topic: dict, kind: str = '') -> str:
    if kind not in ('', 'guide', 'resource', 'glossary'):
        raise ValueError('Unsupported finder source type')
    return '/poker/find/#topic=' + topic['id'] + ('&kind=' + kind if kind else '')


def annotate(items: list[dict], topics: list[dict]) -> list[dict]:
    """Add subject membership without changing destinations or approval metadata."""
    glossary = {e['id'].removeprefix('term-') for e in items if e['kind'] == 'glossary'}
    for topic in topics:
        if not set(topic['glossary_terms']) <= glossary:
            raise ValueError('Unknown glossary term in topic map')
    result = []
    for item in items:
        ids = []
        for topic in topics:
            member = (item['kind'] == 'guide' and item['url'] in
                      {g['route'] for g in topic['guides']} | set(topic['overview_routes']) | {'/poker/topics/' + topic['id'] + '/'} )
            member |= (item['kind'] == 'resource' and item['id'].removeprefix('external-') in
                       {r['id'] for r in topic['resources']})
            member |= (item['kind'] == 'glossary' and (topic['id'] == 'learn' or
                       item['id'].removeprefix('term-') in topic['glossary_terms']))
            if member: ids.append(topic['id'])
        labels = ' '.join(t['title'] for t in topics if t['id'] in ids)
        result.append({**item, 'topics': ids, 'keywords': item['keywords'] + ' ' + labels})
    return result


def source_card(source: dict) -> str:
    method = 'Public page read' if source['review_method'] == 'page' else 'Search index only'
    return ('<li class="topic-source" data-topic-source="' + source['id'] + '">'
            '<h4><a href="' + escape(source['url'], quote=True) + '" rel="external">'
            + escape(source['title']) + '</a></h4>'
            '<p class="topic-meta">' + escape(source['publisher'] + ' · ' + source['access'] + ' · ' + source['kind']) + '</p>'
            '<p>' + escape(source['description']) + '</p>'
            + ('<p class="topic-caution"><strong>Before you use it:</strong> ' + escape(source['notes']) + '</p>' if source['notes'] else '')
            + '<p class="topic-meta">' + method + ' · <time datetime="' + source['reviewed_on'] + '">'
            + source['reviewed_on'] + '</time> · <a href="/poker/resources/#resource-' + source['id']
            + '">Full listing</a></p></li>')


def supplement(topics: list[dict]) -> dict[str, str]:
    cards, sections, jumps, options = [], [], [], []
    for index, topic in enumerate(topics, 1):
        ident, title = topic['id'], escape(topic['title'])
        count = f'{len(topic["guides"])} guides · {len(topic["resources"])} outside sources'
        route = '/poker/topics/' + ident + '/'
        starter = '/poker/' + topic['steps'][0]['guide'] + '/'
        cards.append('<article class="topic-card"><p class="topic-number">' + f'{index:02}' + '</p>'
                     '<h3><a href="' + route + '">' + title + '</a></h3><p>' + escape(topic['summary']) + '</p>'
                     '<p class="topic-meta">' + count + '</p><p class="topic-start">Start: <a href="' + starter + '">'
                     + escape(topic['start_label']) + '</a></p></article>')
        jumps.append('<a href="' + route + '">' + title + '</a>')
        options.append('<option value="' + ident + '">' + title + '</option>')
        steps = ''.join('<li><a href="/poker/' + s['guide'] + '/">' + escape(s['label']) + '</a></li>' for s in topic['steps'])
        guides = ''.join('<li><a href="' + g['route'] + '">' + escape(g['title']) + '</a>'
                         '<span class="topic-meta">' + escape(g['level']) + f' · About {g["minutes"]} min</span></li>'
                         for g in topic['guides'])
        support = ('<p class="topic-support"><a href="/poker/resources/#mental-game">Go directly to gambling-support resources</a>. '
                   'You do not need to search, complete a lesson or sign in.</p>' if ident == 'safer-play' else '')
        caution = ('<p class="topic-caution">This is a source directory, not a live schedule, room-availability service or legal eligibility check. '
                   'Confirm current details directly with the organizer or room.</p>' if ident == 'places-to-play' else '')
        source_index = ('<details class="poker-details topic-all-sources"><summary>All ' + str(len(topic['resources'])) + ' outside sources</summary>'
                        '<div><p class="topic-meta">The complete topic list. Access labels describe the linked resource, not every product from the publisher.</p><ul>'
                        + ''.join('<li><a href="' + escape(r['url'], quote=True) + '" rel="external">' + escape(r['title']) + '</a>'
                                  '<span class="topic-meta">' + escape(r['publisher'] + ' · ' + r['access']) + ' · <a href="/poker/resources/#resource-' + r['id'] + '">Listing and review context</a></span></li>'
                                  for r in sorted(topic['resources'], key=lambda r: r['title'].casefold())) + '</ul></div></details>')
        sections.append('<section class="section folio-row topic-section" id="' + ident + '" aria-labelledby="topic-' + ident + '">'
                        '<div class="section-meta"><p class="section-label">Browse / ' + f'{index:02}' + '</p></div>'
                        '<div class="section-content"><h2 class="section-title" id="topic-' + ident + '">' + title + '</h2>'
                        '<p class="section-deck">' + escape(topic['summary']) + '</p>' + support + caution
                        + '<div class="topic-columns"><div><h3>Start with a question</h3><ol class="topic-steps">' + steps + '</ol>'
                        '<details class="poker-details topic-guides"><summary>All ' + str(len(topic['guides'])) + ' guides on this topic</summary>'
                        '<ul>' + guides + '</ul></details><p><a href="' + escape(finder_url(topic, 'guide'), quote=True)
                        + '">Search on-site material in this topic</a></p></div>'
                        '<div><h3>Selected outside sources</h3><p class="topic-meta">Editorial starting points, not a ranking.</p><ul class="topic-sources">'
                        + ''.join(source_card(r) for r in topic['featured']) + '</ul>' + source_index
                        + '<p><a href="' + escape(finder_url(topic, 'resource'), quote=True) + '">Browse all '
                        + str(len(topic['resources'])) + ' outside sources in this topic</a></p></div></div>'
                        '<div class="topic-return"><a href="' + escape(finder_url(topic), quote=True) + '">Search this topic</a>'
                        '<a href="/poker/topics/">Back to all topics</a></div></div></section>')
    return {'poker_topic_cards': '<div class="topic-grid">' + ''.join(cards) + '</div>',
            'poker_topic_sections': '\n'.join(sections), 'poker_topic_count': str(len(topics)),
            'poker_topic_jumps': '<nav class="topic-jumps" aria-label="Poker topics">' + ''.join(jumps) + '</nav>',
            'poker_topic_options': ''.join(options)}


def detail(topic: dict) -> str:
    """One bounded topic per page, rather than thirty source cards in one index."""
    markup = supplement([topic])['poker_topic_sections']
    # The shared page header already contains this subject's name.
    markup = markup.replace('Browse / 01', 'Read / Compare / Continue')
    markup = markup.replace('>' + escape(topic['title']) + '</h2>', '>A useful starting point.</h2>', 1)
    return markup


def breadcrumb(page: dict, topics: list[dict]) -> str:
    if not page['path'].startswith('/poker/') or page['path'] == '/poker/':
        return ''
    topic = next((t for t in topics if page['path'] in
                  {'/poker/' + s + '/' for s in t['primary_guides']} | set(t['overview_routes'])), None)
    links = '<li><a href="/poker/">Poker</a></li>'
    if page.get('poker_topic'):
        links += '<li><a href="/poker/topics/">Topics</a></li>'
    elif topic:
        links += '<li><a href="/poker/topics/">Topics</a></li><li><a href="/poker/topics/' + topic['id'] + '/">' + escape(topic['title']) + '</a></li>'
    else:
        labels = {'/poker/find/': 'Search', '/poker/topics/': 'Topic map', '/poker/library/': 'Guides',
                  '/poker/resources/': 'External resources', '/poker/resource-quality/': 'Resource review record',
                  '/poker/study-calculators/': 'Study calculators', '/poker/tournament-checklists/': 'Planning sheets'}
        links += '<li><span>' + escape(labels.get(page['path'], page['title'])) + '</span></li>'
    return '<nav class="poker-breadcrumb" aria-label="Breadcrumb"><ol>' + links + '</ol></nav>'


def related_topic(page: dict, topics: list[dict]) -> str:
    topic = next((t for t in topics if page['path'] in
                  {'/poker/' + slug + '/' for slug in t['primary_guides']}), None)
    if not topic:
        return ''
    return ('<nav class="shell topic-context" aria-label="Explore this poker subject">'
            '<p>More in <a href="/poker/topics/' + topic['id'] + '/">' + escape(topic['title']) + '</a>: '
            '<a href="' + escape(finder_url(topic, 'resource'), quote=True) + '">compare outside sources</a>'
            ' or <a href="/poker/topics/">choose another topic</a>.</p></nav>')
