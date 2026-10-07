"""Public-only poker catalog. Plain text in, escaped static pages out.

Unpublished drafts must live outside the repository, not in this catalog.
No network calls, runtime database, remote thumbnails, or automatic publishing.
"""
from __future__ import annotations
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from email.utils import formatdate
from xml.etree import ElementTree as ET
import calendar
import json
import re

KINDS = {'episode': 'episodes', 'hand': 'hands', 'story': 'stories'}
LABELS = {'episode': 'Episode companion', 'hand': 'Hand review', 'story': 'Tournament story'}
CORE = {'slug', 'kind', 'title', 'summary', 'published', 'approved', 'sections'}
OPTIONAL = {'updated', 'revision', 'video_url', 'duration_seconds', 'chapters', 'related', 'spoiler', 'image', 'record_type', 'context', 'sources'}

def txt(value: str, label: str, limit: int = 6000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f'{label} must be nonempty text (at most {limit} characters)')
    if any(ord(c) < 32 and c not in '\n\t' for c in value) or '\u2014' in value:
        raise ValueError(f'{label} contains unsupported punctuation or control characters')
    return value.strip()

def day(value: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Publication and update dates must use YYYY-MM-DD')
    return date.fromisoformat(value)

def youtube_id(url: str) -> str:
    if not isinstance(url, str):
        raise ValueError('Video URL must be text')
    u = urlsplit(url)
    if u.scheme != 'https' or u.username or u.password or u.port or u.fragment:
        raise ValueError('Use a standard HTTPS YouTube video URL')
    if u.netloc in ('www.youtube.com', 'youtube.com') and u.path == '/watch':
        values = parse_qs(u.query)
        vid = values.get('v', [''])[0] if len(values.get('v', [])) == 1 else ''
    elif u.netloc == 'youtu.be':
        vid = u.path.lstrip('/')
    else:
        vid = ''
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}', vid):
        raise ValueError('Use a YouTube watch or youtu.be URL for one video')
    return vid

def video_link(entry: dict, seconds: int | None = None) -> str:
    url = 'https://www.youtube.com/watch?v=' + youtube_id(entry['video_url'])
    return url + (f'&t={seconds}s' if seconds is not None else '')

def route(entry: dict) -> str:
    return f'/poker/{KINDS[entry["kind"]]}/{entry["slug"]}/'

def clock(seconds: int) -> str:
    return (f'{seconds // 3600}:{seconds % 3600 // 60:02}:{seconds % 60:02}'
            if seconds >= 3600 else f'{seconds // 60}:{seconds % 60:02}')

def paragraphs(values: list, label: str) -> None:
    if not isinstance(values, list) or not 1 <= len(values) <= 40:
        raise ValueError(f'{label} needs 1..40 paragraphs')
    for value in values:
        txt(value, label)

def load(root: Path, *, as_of: date | None = None) -> dict:
    if as_of is None:
        as_of = datetime.now(timezone.utc).date()
    if type(as_of) is not date:
        raise TypeError('as_of must be a date')
    path = root / '_source/poker/catalog.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'version', 'entries'} or type(data['version']) is not int or data['version'] != 1:
        raise ValueError('Poker catalog must contain version 1 and entries only')
    entries = data['entries']
    if not isinstance(entries, list):
        raise ValueError('Poker entries must be a list')
    seen = set()
    for e in entries:
        if not isinstance(e, dict) or not CORE <= set(e) or set(e) - CORE - OPTIONAL:
            raise ValueError('Poker entry has missing or unknown fields; keep private drafts outside the repository')
        if e['approved'] is not True:
            raise ValueError('Only explicitly approved public entries belong in the catalog')
        if e['kind'] not in KINDS or not isinstance(e['slug'], str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', e['slug']):
            raise ValueError('Invalid poker kind or slug')
        if e['slug'] in seen:
            raise ValueError('Poker slugs must be unique across all content types')
        seen.add(e['slug'])
        txt(e['title'], 'Title', 140); txt(e['summary'], 'Summary', 320)
        published = day(e['published'])
        if published > as_of:
            raise ValueError('Publication date cannot be in the future; this site does not schedule releases')
        if 'updated' in e:
            updated = day(e['updated'])
            if updated > as_of:
                raise ValueError('Update date cannot be in the future; this site does not schedule releases')
            if updated < published:
                raise ValueError('An update cannot precede publication')
            txt(e.get('revision', ''), 'Revision', 500)
        elif 'revision' in e:
            raise ValueError('A revision needs an update date')
        sections = e['sections']
        if not isinstance(sections, list) or not 1 <= len(sections) <= 20:
            raise ValueError('Provide 1..20 article sections')
        for section in sections:
            if not isinstance(section, dict) or set(section) != {'heading', 'paragraphs'}:
                raise ValueError('Sections contain heading and paragraphs only')
            txt(section['heading'], 'Section heading', 140)
            paragraphs(section['paragraphs'], 'Section')
        if 'spoiler' in e:
            paragraphs(e['spoiler'], 'Result and later review')
        if 'context' in e:
            txt(e['context'], 'Context', 500)
        if e['kind'] == 'hand' and e.get('record_type') not in ('reconstructed', 'illustrative'):
            raise ValueError('Hand reviews must be labeled reconstructed or illustrative')
        if 'record_type' in e and e['kind'] != 'hand':
            raise ValueError('record_type is only for hands')
        if e['kind'] == 'episode' and not e.get('video_url'):
            raise ValueError('Episodes need an approved, publicly playable YouTube link')
        if 'video_url' in e:
            youtube_id(e['video_url'])
            duration = e.get('duration_seconds')
            if type(duration) is not int or not 1 <= duration <= 43200:
                raise ValueError('Video duration_seconds must be an integer from 1 to 43200')
        elif 'duration_seconds' in e or 'chapters' in e:
            raise ValueError('Duration and chapters need a video')
        chapters = e.get('chapters', [])
        if not isinstance(chapters, list):
            raise ValueError('Chapters must be a list')
        previous = -1
        for i, chapter in enumerate(chapters):
            if not isinstance(chapter, dict) or set(chapter) != {'seconds', 'title'}:
                raise ValueError('Chapters need seconds and title')
            t = chapter['seconds']
            if type(t) is not int or not previous < t < e['duration_seconds'] or (i == 0 and t != 0):
                raise ValueError('Chapters must start at zero, increase, and fit inside the video')
            txt(chapter['title'], 'Chapter title', 120)
            previous = t
        related = e.get('related', [])
        if not isinstance(related, list) or any(not isinstance(x, str) for x in related) or len(related) != len(set(related)):
            raise ValueError('Related slugs must be a unique list')
        if 'image' in e:
            image = e['image']
            if not isinstance(image, dict) or set(image) != {'src', 'alt', 'width', 'height'}:
                raise ValueError('An image needs src, alt, width and height')
            src = image['src']
            if not isinstance(src, str) or not re.fullmatch(r'/assets/poker/[a-z0-9-]+\.(?:jpg|jpeg|png|webp)', src):
                raise ValueError('Use a locally hosted image under /assets/poker/')
            image_path = (root / src.lstrip('/')).resolve()
            if not image_path.is_relative_to(root.resolve()) or not image_path.is_file():
                raise ValueError('Poker image must exist within the repository')
            for dimension in ['width', 'height']:
                if type(image[dimension]) is not int or not 1 <= image[dimension] <= 10000:
                    raise ValueError('Image dimensions must be positive pixel counts')
            txt(image['alt'], 'Image alternative text', 400)
        sources = e.get('sources', [])
        if not isinstance(sources, list):
            raise ValueError('Sources must be a list')
        for source in sources:
            if not isinstance(source, dict) or set(source) != {'label', 'url'}:
                raise ValueError('A source needs label and url')
            txt(source['label'], 'Source label', 160)
            u = urlsplit(txt(source['url'], 'Source URL', 2000))
            if u.scheme != 'https' or not u.hostname or u.username or u.password:
                raise ValueError('Source links must be public HTTPS URLs')
    for e in entries:
        for slug in e.get('related', []):
            if slug not in seen or slug == e['slug']:
                raise ValueError('Related items must name another approved catalog entry')
    data['entries'] = sorted(entries, key=lambda e: (e['published'], e['slug']), reverse=True)
    return data

def manifest(data: dict) -> list[dict]:
    return [{'id': 'poker-' + e['kind'] + '-' + e['slug'], 'path': route(e), 'title': e['title'],
             'seo_title': e['title'] + ' | Nolan Kido Poker', 'description': e['summary'],
             'section': 'poker', 'kicker': LABELS[e['kind']], 'poker_entry': e['slug'],
             'date': e['published'], **({'updated': e['updated']} if 'updated' in e else {})}
            for e in data['entries']]

def paragraph_html(values: list) -> str:
    return ''.join('<p>' + escape(v) + '</p>' for v in values)

def image_html(e: dict) -> str:
    if 'image' not in e:
        return ''
    i = e['image']
    return (f'<img class="poker-editorial-image" src="{escape(i["src"], quote=True)}" '
            f'alt="{escape(i["alt"], quote=True)}" width="{i["width"]}" height="{i["height"]}" loading="lazy">')

def card(e: dict) -> str:
    return (f'<article class="poker-content-card"><p class="note-category">{LABELS[e["kind"]]}</p>'
            f'<h3><a href="{route(e)}">{escape(e["title"])}</a></h3>'
            f'<p>{escape(e["summary"])}</p><p class="small-copy">'
            f'<time datetime="{e["published"]}">{e["published"]}</time></p></article>')

def supplement(data: dict, root: Path) -> dict:
    entries = data['entries']
    if entries:
        cards = '<div class="poker-content-grid">' + ''.join(card(e) for e in entries[:6]) + '</div>'
        if len(entries) > 6:
            cards += '<details class="poker-details"><summary>Earlier stories and episodes</summary>' + ''.join(card(e) for e in entries[6:]) + '</details>'
    else:
        cards = ('<div class="poker-first-read"><p class="note-category">A starting point</p>'
                 '<h3><a href="/poker/reviewing-a-hand/">Review a hand, not just the result.</a></h3>'
                 '<p>A worked, clearly fictional hand shows how to keep the action, original thinking, and later analysis separate.</p>'
                 '<p class="small-copy">No vlog episodes or tournament stories are published on this site yet. '
                 'This guide and the study resources below are available now.</p></div>')
    return {'poker_collection': cards,
            'poker_hand_sheet': escape((root / 'downloads/poker-hand-review.md').read_text()),
            'poker_debrief_sheet': escape((root / 'downloads/poker-session-debrief.md').read_text())}

def render(e: dict, data: dict) -> str:
    parts = ['<div class="article-body shell prose poker-entry">',
             f'<p class="note-meta">Published <time datetime="{e["published"]}">{e["published"]}</time> · Nolan Kido</p>',
             '<p class="article-lead">' + escape(e['summary']) + '</p>']
    if e.get('record_type'):
        parts.append('<p class="poker-context">' + ('Illustrative hand. This did not occur in a recorded session.'
                     if e['record_type'] == 'illustrative' else 'Reconstructed hand. Recalled details and estimates are identified in the account.') + '</p>')
    if e.get('context'):
        parts.append('<p class="poker-context">' + escape(e['context']) + '</p>')
    parts.append(image_html(e))
    if e.get('video_url'):
        parts.append(f'<div class="poker-watch"><a class="button" href="{escape(video_link(e), quote=True)}">Watch on YouTube</a>'
                     f'<p class="small-copy">{clock(e["duration_seconds"])}. Playback opens on YouTube. No video or remote thumbnail loads on this page.</p></div>')
        if e.get('chapters'):
            parts.append('<nav class="poker-chapters" aria-label="Video chapters"><h2>Jump to a moment</h2><ol>')
            for chapter in e['chapters']:
                parts.append(f'<li><a href="{escape(video_link(e, chapter["seconds"]), quote=True)}">'
                             f'<span>{clock(chapter["seconds"])}</span> {escape(chapter["title"])}</a></li>')
            parts.append('</ol></nav>')
    if len(e['sections']) > 2:
        parts.append('<nav class="poker-jump" aria-label="On this page">' + ''.join(
            f'<a href="#section-{i}">{escape(s["heading"])}</a>' for i, s in enumerate(e['sections'], 1)) + '</nav>')
    for i, section in enumerate(e['sections'], 1):
        parts.append(f'<section aria-labelledby="section-{i}"><h2 id="section-{i}">{escape(section["heading"])}</h2>' + paragraph_html(section['paragraphs']) + '</section>')
    if e.get('spoiler'):
        parts.append('<details class="poker-details"><summary>Result and later review (spoilers)</summary><div>' + paragraph_html(e['spoiler']) + '</div></details>')
    if e.get('sources'):
        parts.append('<h2>Sources and references</h2><ul>' + ''.join(
            f'<li><a href="{escape(s["url"], quote=True)}">{escape(s["label"])}</a></li>' for s in e['sources']) + '</ul>')
    if e.get('revision'):
        parts.append('<p class="editorial-note">Updated ' + e['updated'] + ': ' + escape(e['revision']) + '</p>')
    related = [x for x in data['entries'] if x['slug'] in e.get('related', []) or e['slug'] in x.get('related', [])]
    if related:
        parts.append('<section><h2>Related hands and stories</h2>' + ''.join(card(x) for x in related) + '</section>')
    parts.append('<p class="editorial-note">Prepared with AI assistance and approved for public release. '
                 'Estimates and later interpretations should be read in the context of the account, not as verified strategy advice.</p>'
                 '<nav class="article-navigation" aria-label="After this poker story"><a href="/poker/#watch">More from Poker</a>'
                 '<a href="/poker/start-here/">Reading the action</a><a href="/poker/glossary/">Poker glossary</a><a href="/contact/">Send a correction or thought</a></nav></div>')
    return ''.join(parts)

def feed(pages: list, origin: str) -> str:
    ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
    rss = ET.Element('rss', {'version': '2.0'}); channel = ET.SubElement(rss, 'channel')
    for k, v in [('title', 'Nolan Kido Poker'), ('link', origin + '/poker/'),
                 ('description', 'Poker episodes, hand reviews, stories, and reading guides.'), ('language', 'en-us')]:
        ET.SubElement(channel, k).text = v
    ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link', {'href': origin + '/poker/feed.xml', 'rel': 'self', 'type': 'application/rss+xml'})
    eligible = [p for p in pages if p['path'].startswith('/poker/') and p.get('date') and not p.get('noindex')]
    for p in sorted(eligible, key=lambda p: (p['date'], p['id']), reverse=True):
        item = ET.SubElement(channel, 'item')
        for k, v in [('title', p['title']), ('link', origin + p['path']), ('description', p['description'])]:
            ET.SubElement(item, k).text = v
        ET.SubElement(item, 'guid', {'isPermaLink': 'true'}).text = origin + p['path']
        ET.SubElement(item, 'pubDate').text = formatdate(calendar.timegm(day(p['date']).timetuple()), usegmt=True)
    ET.indent(rss, space='  ')
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(rss, encoding='unicode') + '\n'
