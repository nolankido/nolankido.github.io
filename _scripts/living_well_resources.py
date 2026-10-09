"""Small, curated, static Living Well resource collection. No browser state or input."""
from __future__ import annotations
from datetime import date
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

PREFIX = '/living-well/'
ACCESS = {
    'web': 'Free to browse',
    'app': 'Free app',
    'account': 'Free with an account',
    'library': 'Library card required',
    'interactive': 'Free browser interactive',
}
TOPIC_SHELVES = {'meaning': 'meaning', 'attention': 'attention', 'everyday-ai': 'everyday-ai',
                'relationships': 'care', 'choices': 'thinking'}


def safe_url(value: str) -> str:
    if not isinstance(value, str) or any(c.isspace() for c in value):
        raise ValueError('Resource URLs must be whitespace-free strings')
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Resource URLs require HTTPS without credentials')
    return value


def load(root: Path) -> dict:
    data = json.loads((root / '_source/living-well/resources.json').read_text(encoding='utf-8'))
    if data.get('version') != 1:
        raise ValueError('Unknown Living Well resource catalog version')
    date.fromisoformat(data['reviewed_on'])
    shelf_ids = [s['id'] for s in data['shelves']]
    if any(not isinstance(i, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', i) for i in shelf_ids):
        raise ValueError('Invalid Living Well shelf ID')
    if len(shelf_ids) != len(set(shelf_ids)):
        raise ValueError('Duplicate Living Well shelf')
    seen = set()
    destinations = set()
    for entry in data['resources']:
        ident = entry['id']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident in seen:
            raise ValueError('Invalid or duplicate resource ID')
        seen.add(ident)
        if entry['shelf'] not in shelf_ids or entry['access'] not in ACCESS:
            raise ValueError('Unknown resource shelf or access type')
        if entry['status'] != 'published-selection':
            raise ValueError('Unreviewed resource in public catalog')
        for field in ('title', 'creator', 'entry_title', 'requirements', 'format', 'why', 'start', 'limit', 'review_scope'):
            if not isinstance(entry[field], str) or not entry[field].strip():
                raise ValueError('Missing resource editorial field: ' + field)
        for field in ('url', 'entry_url', 'verification_url'):
            safe_url(entry[field])
        if entry['entry_url'] in destinations:
            raise ValueError('Duplicate resource starting point')
        destinations.add(entry['entry_url'])
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', entry['companion']):
            raise ValueError('Invalid companion route')
        reviewed = date.fromisoformat(entry['reviewed_on'])
        if reviewed > date.fromisoformat(data['reviewed_on']):
            raise ValueError('Resource review exceeds collection date')
    for shelf in data['shelves']:
        matches = [e for e in data['resources'] if e['shelf'] == shelf['id']]
        if not matches or shelf['start_id'] not in {e['id'] for e in matches}:
            raise ValueError('Every shelf needs a valid first selection')
    return data


def external(url: str, label: str) -> str:
    return '<a href="' + escape(safe_url(url), quote=True) + '">' + escape(label) + '</a>'


def resource_card(entry: dict, compact: bool = False) -> str:
    e = lambda field: escape(entry[field])
    label = escape(ACCESS[entry['access']])
    if compact:
        return ('<article class="lw-card lw-resource-preview"><p class="lw-eyebrow">' + e('format')
                + '</p><h3><a href="/living-well/free-resources/#' + e('id') + '">' + e('title')
                + '</a></h3><p>' + e('why') + '</p><p class="lw-access">' + label + '</p></article>')
    return ('<article class="lw-card lw-resource" id="' + e('id') + '"><p class="lw-eyebrow">'
            + e('format') + ' · ' + label + '</p><h3>' + e('title') + '</h3>'
            + '<p class="lw-creator">' + e('creator') + '</p><p>' + e('why') + '</p>'
            + '<p><strong>Begin here:</strong> ' + e('start') + '</p>'
            + '<p class="lw-access"><strong>Access:</strong> ' + e('requirements') + '</p>'
            + '<p>' + external(entry['entry_url'], entry['entry_title']) + '</p>'
            + '<details class="lw-resource-notes"><summary>Before you go</summary><p>' + e('limit') + '</p>'
            + '<p><a href="/living-well/' + e('companion') + '/">Related reading on Living Well</a></p>'
            + '<p class="small-copy">Public source reviewed <time datetime="' + e('reviewed_on') + '">'
            + e('reviewed_on') + '</time>. ' + external(entry['verification_url'], 'Provider details')
            + '. No claim of firsthand use or a completed course.</p></details></article>')


def render(root: Path, section) -> str:
    data = load(root)
    by_id = {e['id']: e for e in data['resources']}
    jumps = '<nav class="lw-shelf-jumps" aria-label="Free resource collections">' + ''.join(
        '<a href="#shelf-' + escape(s['id']) + '">' + escape(s['title']) + '</a>' for s in data['shelves']) + '</nav>'
    body = section('choose-one', 'A place to begin', 'Something worth your attention.',
        '<p class="lw-lead">18 free starting points, not a list to finish.</p>'
        '<p class="section-deck">Listen to a conversation, try a small practice, understand a tool, or find a book. '
        'Each selection explains why it belongs here and what you need before opening it.</p>'
        '<p>All Living Well pages are free and need no account. Outside resources have their own access requirements, '
        'shown below. These are editorial selections, not a list of tools Nolan claims to have used.</p>' + jumps)
    body += section('without-signing-up', 'No new account', 'Only choosing one?',
        '<div class="lw-situations"><p><span>Something to hear or read</span><a href="#on-being">'
        'An On Being conversation</a></p><p><span>Something small to try</span><a href="#ucla-mindful">'
        'A short UCLA recording or transcript</a></p><p><span>Something to understand</span>'
        '<a href="#how-ai-works">An introduction to how AI works</a></p></div>')
    for shelf in data['shelves']:
        first = by_id[shelf['start_id']]
        intro = '<p class="section-deck">' + escape(shelf['intro']) + '</p><p class="small-copy">Start with <a href="#'
        intro += escape(first['id']) + '">' + escape(first['title']) + '</a> when you would rather choose just one.</p>'
        body += section('shelf-' + shelf['id'], 'Selected resources', escape(shelf['title']), intro
            + '<div class="lw-cards lw-resource-grid">' + ''.join(resource_card(e) for e in data['resources'] if e['shelf'] == shelf['id']) + '</div>'
            + '<p class="lw-back"><a href="#choose-one">Back to the collection choices</a></p>')
    body += section('about-this-collection', 'How this is selected', 'Free does not mean identical access.',
        '<div class="prose"><p><strong>Free to browse</strong> means the selected public material can be read or opened without a paid plan. '
        '<strong>Free app</strong> may still require installation and setup. <strong>Free with an account</strong> '
        'requires registration. <strong>Library card required</strong> depends on your library and eligibility. '
        'A free course does not make every tool it demonstrates free.</p>'
        '<p>Public provider pages and access information were reviewed on October 9, 2026. Apps have not been installed, '
        'courses have not been completed, and every media player or regional access path has not been tested. '
        'These are not security audits or personal testimonials. External sites have their own privacy practices.</p>'
        '<p>The annotations are original; the linked work stays with its creators. There are no affiliate links in '
        'this collection. A free resource is not necessarily licensed for republication.</p>'
        '<p><a href="/living-well/sources/">Sources behind our articles</a> are kept separate from this browsing collection. '
        'Found a changed access requirement? <a href="/contact/">Send a correction</a>.</p></div>')
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
    body += section('start-where-you-are', 'Questions to explore', 'Start with a question.',
        '<div class="lw-situations"><p><span>Can something matter before you can explain it?</span>'
        '<a href="/living-well/spiritual-curiosity-reading-path/">Explore spiritual curiosity</a></p>'
        '<p><span>When does technology give us more room to live?</span>'
        '<a href="/living-well/technology-that-helps-you-notice/">A tool that helps you notice more</a></p>'
        '<p><span>Can you grow without treating yourself as a problem?</span>'
        '<a href="/living-well/growth-without-self-rejection/">Improvement without self-rejection</a></p></div>')
    body += section('three-free-starts', 'Read · try · explore', 'A few worthwhile places to go.',
        '<div class="lw-cards lw-three">' + ''.join(resource_card(resources[i], True) for i in ['on-being','ucla-mindful','seek'])
        + '</div><p><a href="/living-well/free-resources/">Browse all 18 free resources and their access notes</a></p>')
    body += section('choose-a-route', 'Read or try', 'One idea. One useful example.',
        '<div class="lw-routes lw-two"><article class="lw-route"><p class="lw-eyebrow">Explore an idea</p>'
        '<h3><a href="/living-well/ideas/">Essays &amp; reading paths</a></h3><p>Meaning, attention, and questions that '
        'do not need a quick answer.</p></article><article class="lw-route"><p class="lw-eyebrow">Try something</p>'
        '<h3><a href="/living-well/guides/">Practical guides</a></h3><p>Small examples, tools, and optional exercises '
        'for an ordinary day.</p></article></div>'
        + '<span id="first-collection"></span>' + cards([by_slug['technology-that-helps-you-notice'], by_slug['weekly-reset']]))
    body += section('five-subjects', 'Browse by subject', 'Follow what interests you.', topic_cards())
    body += section('a-small-invitation', 'Keep exploring', 'No program to keep up with.',
        '<p class="section-deck">Read, listen, try something, or close the page and take the question with you. '
        'There is nothing to submit and no streak to maintain.</p><div class="link-row">'
        '<a href="/living-well/worksheets/">Private-use worksheets</a><a href="/living-well/conversations/">'
        'A conversation worth having</a><a href="/living-well/field-notes/">Proposed experiments</a></div>'
        '<p class="small-copy"><a href="/living-well/editorial-standards/">Editorial standards and AI assistance</a> · '
        '<a href="/living-well/feed.xml">Living Well RSS</a>. No firsthand experiment results have been published yet.</p>')
    return body


def related_shelf(topic: str) -> str:
    shelf = TOPIC_SHELVES[topic]
    return '<p><a href="/living-well/free-resources/#shelf-' + shelf + '">Explore selected free resources for this subject</a></p>'
