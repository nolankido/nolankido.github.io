"""Discover existing practical work and publish its real articles, without new claims.

Tool pages are not feed articles. The Technology feed includes explicitly selected
Notes and all published Technology evidence articles; combined-feed deduplication
retains the original source records. No network, accounts, or runtime scripts.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
import json
from pathlib import Path
import re
import struct
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

FEED = Path('technology/feed.xml')
TITLE = 'Nolan Kido | Practical AI writing'
DESCRIPTION = 'Essays and recorded cases about practical AI, checking results, and human judgment. Tools and website edits are not new articles.'
SCOPED_IDS = frozenset({'home', 'technology', 'notes'})
TOOL_IDS = frozenset({'task-brief', 'ai-time-savings'})


def articles(pages: list[dict]) -> list[dict]:
    """Evidence articles have explicit dates and an existing canonical source."""
    result = []
    for page in pages:
        if page.get('section') != 'technology' or not page.get('evidence_article'):
            continue
        if page.get('noindex') or page.get('draft') or page.get('living_well_kind') == 'experiment':
            raise ValueError('Technology articles must be published, indexable content')
        if not isinstance(page.get('date'), str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', page['date']):
            raise ValueError('Technology article needs an explicit publication date')
        datetime.strptime(page['date'], '%Y-%m-%d')
        for key in ('title', 'description', 'path', 'source'):
            if not isinstance(page.get(key), str) or not page[key].strip():
                raise ValueError('Technology article is missing ' + key)
        if not re.fullmatch(r'/technology/(?:[a-z0-9-]+/)+', page['path']):
            raise ValueError('Technology article needs a canonical Technology route')
        result.append(deepcopy(page))
    if len({p['path'] for p in result}) != len(result):
        raise ValueError('Duplicate Technology article')
    return sorted(result, key=lambda p: (p['date'], p['path']), reverse=True)


def load(root: Path, pages: list[dict]) -> dict:
    config = json.loads((root / '_source/practical-discovery.json').read_text(encoding='utf-8'))
    if not isinstance(config, dict):
        raise ValueError('Practical discovery needs an object')
    by_id = {p['id']: p for p in pages}
    eligible = {p['id'] for p in articles(pages)}
    works = config.get('works')
    if not isinstance(works, list) or len(works) != 3:
        raise ValueError('Select three existing works')
    ids = []
    for work in works:
        if not isinstance(work, dict) or any(not isinstance(work.get(k), str) or not work[k].strip()
                                               for k in ('id', 'label', 'summary', 'action', 'home_label')):
            raise ValueError('Work needs an identity and descriptive reader labels')
        page = by_id.get(work['id'])
        if not page or page.get('noindex') or page.get('draft') or page.get('section') != 'technology':
            raise ValueError('Work must be an existing public Technology page')
        ids.append(work['id'])
        kind = work.get('kind')
        if (kind not in {'tool', 'case'} or (kind == 'case') != (work['id'] in eligible)
                or (kind == 'tool' and work['id'] not in TOOL_IDS)):
            raise ValueError('Work type must match the published page')
        image = work.get('image')
        if image is not None:
            if kind != 'tool' or not isinstance(image, dict):
                raise ValueError('These previews belong to the actual tools only')
            src = image.get('src')
            if not isinstance(src, str) or not re.fullmatch(r'/assets/work/[a-z0-9-]+\.png', src):
                raise ValueError('Work preview must be a local PNG')
            for key in ('alt', 'caption'):
                if not isinstance(image.get(key), str) or not image[key].strip():
                    raise ValueError('Work preview needs an honest caption and alternative text')
            image_path = (root / src.lstrip('/')).resolve()
            if not image_path.is_relative_to((root / 'assets/work').resolve()):
                raise ValueError('Work preview must remain in the local asset directory')
            raw = image_path.read_bytes()
            if not 33 <= len(raw) <= 160_000 or raw[:16] != b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR':
                raise ValueError('Invalid or oversized work preview')
            if struct.unpack('>II', raw[16:24]) != (image.get('width'), image.get('height')):
                raise ValueError('Work preview dimensions disagree')
    if len(set(ids)) != len(ids) or set(ids) != TOOL_IDS | {'ai-website-verification'}:
        raise ValueError('Practical work selection must not duplicate pages')
    selected = config.get('note_ids')
    if (not isinstance(selected, list) or not selected or any(not isinstance(n, str) for n in selected)
            or len(selected) != len(set(selected))):
        raise ValueError('Select distinct existing practical AI essays')
    for id_ in selected:
        p = by_id.get(id_)
        if not p or not p.get('note') or p.get('noindex') or not p.get('date'):
            raise ValueError('Practical AI essay must be a published Note')
    return config


def home_links(config: dict, pages: list[dict]) -> str:
    by_id = {p['id']: p for p in pages}
    links = ''.join('<a href="' + escape(by_id[w['id']]['path'], quote=True) + '">' + escape(w['home_label']) + '</a>' for w in config['works'])
    return ('<aside class="practical-home" aria-labelledby="practical-home-title"><h3 id="practical-home-title">See the work behind the ideas.</h3>'
            '<p>Two free browser tools and one recorded case. Try a task, inspect a result, or check the reasoning.</p>'
            '<nav aria-label="Selected practical AI work">' + links + '</nav></aside>')


def work_cards(config: dict, pages: list[dict]) -> str:
    by_id = {p['id']: p for p in pages}
    cards = []
    for w in config['works']:
        p = by_id[w['id']]
        body = ('<p class="work-kind">' + escape(w['label']) + '</p><h3><a href="' + escape(p['path'], quote=True) + '">' + escape(p['title']) + '</a></h3>'
                '<p>' + escape(w['summary']) + '</p><p><a class="work-action" href="' + escape(p['path'], quote=True) + '">' + escape(w['action']) + '</a></p>')
        if w.get('image'):
            i = w['image']
            body += ('<figure class="work-preview"><img src="' + escape(i['src'], quote=True) + '" width="' + str(i['width']) + '" height="' + str(i['height']) + '" alt="' + escape(i['alt'], quote=True) + '" loading="lazy" decoding="async">'
                     '<figcaption>' + escape(i['caption']) + ' <a href="' + escape(i['src'], quote=True) + '">View the ' + ('brief' if w['id'] == 'task-brief' else 'calculator') + ' preview at full size</a>.</figcaption></figure>')
        else:
            when = datetime.strptime(p['date'], '%Y-%m-%d')
            label = f'{when.strftime("%B")} {when.day}, {when.year}'
            body += '<p class="work-date">Published <time datetime="' + p['date'] + '">' + label + '</time> · Recorded website case, not a productivity study.</p>'
        cards.append('<article class="practical-work work-' + w['kind'] + '">' + body + '</article>')
    return '<div class="practical-work-grid">' + ''.join(cards) + '</div>'


def article_cards(pages: list[dict]) -> str:
    """All Technology cases appear in the existing Writing gateway."""
    cards = []
    for p in articles(pages):
        when = datetime.strptime(p['date'], '%Y-%m-%d')
        label = f'{when.strftime("%B")} {when.day}, {when.year}'
        cards.append('<article class="note-entry technology-publication"><p class="note-category">Recorded case study / Practical AI</p><h3><a href="' + escape(p['path'], quote=True) + '">' + escape(p['title']) + '</a></h3><p>' + escape(p['description']) + '</p><p class="reading-date">Published <time datetime="' + p['date'] + '">' + label + '</time></p></article>')
    return ''.join(cards)


def feed(config: dict, pages: list[dict], outputs: dict, origin: str) -> str:
    parsed = urlsplit(origin)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.path or parsed.query or parsed.fragment:
        raise ValueError('Practical AI feed needs a canonical HTTPS origin')
    by_id = {p['id']: p for p in pages}
    originals = {i.findtext('link'): i for i in ET.fromstring(outputs[Path('feed.xml')]).findall('./channel/item')}
    items = {}
    for id_ in config['note_ids']:
        p = by_id.get(id_)
        if not p or not p.get('note') or p.get('noindex'):
            raise ValueError('Invalid practical AI essay')
        url = origin + p['path']
        if url not in originals:
            raise ValueError('Selected essay missing from its source feed')
        items[url] = (p['date'], deepcopy(originals[url]))
    for p in articles(pages):
        url = origin + p['path']
        if url in items:
            raise ValueError('Duplicate practical AI publication')
        item = ET.Element('item')
        for tag, value in [('title', p['title']), ('link', url), ('description', p['description'])]:
            ET.SubElement(item, tag).text = value
        ET.SubElement(item, 'guid', {'isPermaLink': 'true'}).text = url
        ET.SubElement(item, 'pubDate').text = format_datetime(datetime.strptime(p['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc), usegmt=True)
        items[url] = (p['date'], item)
    ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
    rss = ET.Element('rss', {'version': '2.0'}); ch = ET.SubElement(rss, 'channel')
    for tag, value in [('title', TITLE), ('link', origin + '/technology/'), ('description', DESCRIPTION), ('language', 'en-us')]:
        ET.SubElement(ch, tag).text = value
    ET.SubElement(ch, '{http://www.w3.org/2005/Atom}link', {'href': origin + '/' + FEED.as_posix(), 'rel': 'self', 'type': 'application/rss+xml'})
    for url, (date, item) in sorted(items.items(), key=lambda x: (-datetime.strptime(x[1][0], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp(), x[0])):
        ch.append(item)
    ET.indent(rss, space='  ')
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(rss, encoding='unicode') + '\n'


def article_return(page: dict) -> str:
    if not page.get('evidence_article') or page.get('section') != 'technology':
        return ''
    return ('<section class="section folio-row technology-return" aria-labelledby="case-return-title"><div class="section-meta"><p class="section-label">Read / Keep / Return</p></div><div class="section-content prose">'
            '<h2 id="case-return-title">Keep the method, not just the result.</h2><p>Read the wider argument in <a href="/notes/keep-the-judgment/">Let AI do more. Keep the judgment.</a>, or <a href="/technology/ai-time-savings/">include verification in your workflow time comparison</a>.</p>'
            '<nav class="link-row" aria-label="After the case study"><a href="/notes/#technology">More practical AI writing</a><a href="/follow/#practical-ai-feed">Follow practical AI writing</a><a href="/technology/">Back to Technology</a></nav></div></section>')
