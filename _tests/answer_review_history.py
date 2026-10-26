"""A bounded predecessor view for the answer-review release.

Keep historical golden digests intact. Reverse only this guide's declared
insertions and publication metadata, then let older release adapters run.
The new independent baseline tests also check these reversals against the
actual pre-edit production files and all original rendered page bodies.
"""
from pathlib import Path
from copy import deepcopy
from functools import lru_cache
import json
import re
import search_entry_history

ROOT = Path(__file__).resolve().parents[1]
ID = 'ai-answer-review'
ROUTE = '/technology/check-ai-answers/'
SOURCE = '_source/technology/check-ai-answers.html'
OUTPUT = 'technology/check-ai-answers/index.html'
ADDITION = re.compile(r'<!-- AI answer review: start -->\n.*?<!-- AI answer review: end -->\n', re.S)
HUB_IDS = {'home', 'technology', 'resources'}


@lru_cache(maxsize=1)
def original_manifest():
    baseline = json.loads((ROOT / '_tests/answer-review-baseline.json').read_text())
    return {p['id']: p for p in baseline['manifest']}


def pages(records):
    records = search_entry_history.pages(records)
    original = original_manifest()
    result = [deepcopy(p) for p in records if p['id'] != ID]
    for p in result:
        if p['id'] in HUB_IDS:
            if 'updated' in original[p['id']]: p['updated'] = original[p['id']]['updated']
            else: p.pop('updated', None)
    return result


def before(path, data):
    import practical_ai_print_history
    data = practical_ai_print_history.before(path, data)
    import answer_review_growth_history as growth_history
    data = growth_history.before(path, data)
    data = search_entry_history.before(path, data)
    path = str(path)
    binary = isinstance(data, bytes)
    if not (path.endswith('.html') or path in {'_source/pages.json', '_source/presentation.json',
                                             'technology/feed.xml', 'writing.xml', 'sitemap.xml'}):
        return data
    text = data.decode() if binary else data
    text = ADDITION.sub('', text)
    original = original_manifest()
    if path == '_source/pages.json':
        text = json.dumps(pages(json.loads(text)), indent=2, ensure_ascii=False) + '\n'
    if path == '_source/presentation.json':
        config = json.loads(text)
        config['pages'].pop(ID, None)
        text = json.dumps(config, indent=2) + '\n'
    if path in {'technology/feed.xml', 'writing.xml'}:
        text = re.sub(r'    <item>.*?</item>\n',
                      lambda m: '' if '<link>https://nolankido.com' + ROUTE + '</link>' in m[0] else m[0], text, flags=re.S)
    if path == 'sitemap.xml':
        text = re.sub(r'  <url>.*?</url>\n',
                      lambda m: '' if '<loc>https://nolankido.com' + ROUTE + '</loc>' in m[0] else m[0], text, flags=re.S)
        for key in HUB_IDS:
            p = original[key]
            pattern = r'(<loc>https://nolankido.com' + re.escape(p['path']) + r'</loc>\s*<lastmod>)[^<]+(</lastmod>)'
            text = re.sub(pattern, lambda m: m[1] + p['updated'] + m[2], text)
    if path == 'notes/index.html':
        text = re.sub(r'<article class="note-entry technology-publication">.*?</article>',
                      lambda m: '' if 'href="' + ROUTE + '"' in m[0] else m[0], text, flags=re.S)
    if path == 'find/index.html':
        old = text
        text = re.sub(r'<li class="find-item".*?</li>',
                      lambda m: '' if 'href="' + ROUTE + '"' in m[0] else m[0], text, flags=re.S)
        if old != text:
            pattern = r'(id="browse-technology"><summary>Technology <span class="find-group-count" hidden>\()(\d+)(\)</span>)'
            text = re.sub(pattern, lambda m: m[1] + str(int(m[2]) - 1) + m[3], text)
    for key in HUB_IDS:
        p = original[key]
        output = p['path'].lstrip('/') + 'index.html'
        if path == output:
            text = text.replace('"dateModified": "2026-10-12"', '"dateModified": "' + p['updated'] + '"')
    return text.encode() if binary else text
