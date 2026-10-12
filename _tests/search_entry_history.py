"""Reverse only reviewed entry copy, summaries and preview declarations.

Historical golden digests remain unchanged. The new release tests independently
compare this bounded predecessor view with the untouched production baseline.
"""
from copy import deepcopy
from functools import lru_cache
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
NEW_SOURCES = {'_source/search-entrypoints.json', '_source/reader-previews.json'}
MARKER = re.compile(r'<!-- Reader entry summary: start -->.*?<!-- Reader entry summary: end -->', re.S)
FIELDS = ('title', 'seo_title', 'description', 'updated')


@lru_cache(maxsize=1)
def baseline():
    return json.loads((ROOT / '_tests/search-entry-baseline.json').read_text())


@lru_cache(maxsize=1)
def config():
    return json.loads((ROOT / '_source/search-entrypoints.json').read_text())['entries']


def pages(records):
    original = {p['id']: p for p in baseline()['pages']}
    result = deepcopy(records)
    for p in result:
        if p['id'] in config():
            old = original[p['id']]
            for key in FIELDS:
                if key in old: p[key] = old[key]
                else: p.pop(key, None)
            p.pop('entry_summary', None)
    return result


def before(path, data):
    path = str(path)
    if not path.endswith('.html') and path != 'sitemap.xml':
        return data
    binary = isinstance(data, bytes)
    text = data.decode() if binary else data
    text = MARKER.sub('', text)
    text = re.sub(r'\n  <link rel="stylesheet" href="/assets/search-entrypoints[.]css[?]v=[a-f0-9]{12}">', '', text)
    old_pages = {p['id']: p for p in baseline()['pages']}
    for key, entry in config().items():
        old = old_pages[key]
        route = old['path']
        if 'title' in entry:
            # Only generated destination labels are normalized across other pages.
            label = r'(<a\b[^>]*href="(?:https://nolankido[.]com)?' + re.escape(route) + r'"[^>]*>)' + re.escape(escape(entry['title'])) + r'(</a>)'
            text = re.sub(label, lambda m: m[1] + escape(old['title']) + m[2], text)
        output = route.lstrip('/') + 'index.html'
        if path == output:
            for field in ('seo_title', 'description'):
                text = text.replace(escape(entry[field], quote=True), escape(old[field], quote=True))
            text = text.replace('"name": ' + json.dumps(entry['seo_title'], ensure_ascii=False), '"name": ' + json.dumps(old['seo_title'], ensure_ascii=False))
            if 'title' in entry:
                new, previous = escape(entry['title']), escape(old['title'])
                text = text.replace('<h1 class="page-title">' + new + '</h1>', '<h1 class="page-title">' + previous + '</h1>')
                text = text.replace('<span aria-current="page">' + new + '</span>', '<span aria-current="page">' + previous + '</span>')
                text = text.replace('<span>' + new + '</span>', '<span>' + previous + '</span>')
                text = text.replace(json.dumps(entry['title'], ensure_ascii=False), json.dumps(old['title'], ensure_ascii=False))
            text = text.replace('"description": ' + json.dumps(entry['description'], ensure_ascii=False), '"description": ' + json.dumps(old['description'], ensure_ascii=False))
            text = text.replace('"dateModified": ' + json.dumps(entry['updated']), '"dateModified": ' + json.dumps(old['updated']))
        if path == 'sitemap.xml':
            pattern = r'(<loc>https://nolankido.com' + re.escape(route) + r'</loc>\s*<lastmod>)[^<]+(</lastmod>)'
            text = re.sub(pattern, lambda m: m[1] + old['updated'] + m[2], text)
    if path in baseline()['social'] and '/assets/social/reader-' in text:
        pattern = r'<meta property="og:image".*?<meta name="twitter:image:alt"[^>]*>'
        text = re.sub(pattern, lambda m: baseline()['social'][path], text, flags=re.S)
    if path == 'find/index.html':
        # The finder reuses published summaries verbatim on the matching cards.
        for key, entry in config().items():
            old = old_pages[key]
            pattern = r'(<li class="find-item"[^>]*>.*?href="' + re.escape(old['path']) + r'".*?<p class="find-description">)' + re.escape(escape(entry['description'])) + r'(</p>)'
            text = re.sub(pattern, lambda m: m[1] + escape(old['description']) + m[2], text, flags=re.S)
        # Title changes intentionally alter the alphabetical index order. Restore
        # only order, keeping every item's other bytes available to integrity tests.
        titles = {p['path']: p['title'] for p in baseline()['pages']}
        def group_before(match):
            group = match[0]
            items = re.findall(r'<li class="find-item".*?</li>', group, re.S)
            def key(item):
                route = re.search(r'<h3><a href="([^"]+)"', item)[1]
                return titles.get(route, route).casefold(), route
            ordered = ''.join(sorted(items, key=key))
            return re.sub(r'(<ul class="find-items">).*?(</ul>)', lambda m: m[1] + ordered + m[2], group, flags=re.S)
        text = re.sub(r'<details class="find-group".*?</details>', group_before, text, flags=re.S)
    if path == 'poker/find/index.html':
        for key, entry in config().items():
            if not key.startswith('poker-'): continue
            old = old_pages[key]
            def card_before(match):
                result = match[0]
                for field in ('title', 'description'):
                    if field in entry: result = result.replace(escape(entry[field], quote=True), escape(old[field], quote=True))
                return result
            pattern = r'<article class="reader-card finder-card"[^>]*data-id="' + re.escape(key) + r'".*?</article>'
            text = re.sub(pattern, card_before, text, flags=re.S)
    return text.encode() if binary else text
