"""Styles and representative images for the published project cases.

This module reads only committed public assets. It does not infer ratings,
model quality, visitor outcomes, or the contents of an external demonstration.
"""
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path

CASE_IDS = frozenset({
    'local-ai-review-replies', 'ai-book-continuity-checker', 'dinner-on-time',
    'ai-weekly-reset', 'organize-public-notes', 'local-ai-test-record',
    'ai-poker-video-evidence', 'ai-website-visibility',
    'rightsreceipt-case',
})
SCOPED_IDS = CASE_IDS | {'home', 'technology', 'creative', 'ai-answer-review', 'ai-time-savings', 'ai-workflow-pilot', 'accounting-research'}
IMAGES = {
    'ai-book-continuity-checker': (
        '/assets/projects/preflight-holmes-report.png', 1200, 1349,
        'Archived Preflight report showing source passages for possible Sherlock Holmes continuity errors.',
    ),
    'dinner-on-time': (
        '/assets/projects/dinner-on-time-preview.jpg', 2400, 1396,
        'The public Dinner on Time cooking-planner simulation demonstration.',
    ),
    'rightsreceipt-case': (
        '/assets/projects/rightsreceipt-harbor.svg', 1200, 720,
        'Project-owned fictional Harbor After Rain artwork from the public RightsReceipt demo.',
    ),
}


def head(page, root):
    if page['id'] not in SCOPED_IDS:
        return ''
    assets = ['visibility-projects.css']
    if page['id'] in CASE_IDS:
        assets += ['practical-discovery.css', 'workflow-evidence.css']
    if page['id'] == 'creative':
        assets.append('poker-comics.css')
    links = ''.join(
        '\n  <link rel="stylesheet" href="/assets/' + asset + '?v=' +
        sha256((root / 'assets' / asset).read_bytes()).hexdigest()[:12] + '">'
        for asset in assets
    )
    if page['id'] in {'local-ai-review-replies', 'ai-book-continuity-checker', 'dinner-on-time'}:
        asset = 'project-fragment-arrivals.js'
        version = sha256((root / 'assets' / asset).read_bytes()).hexdigest()[:12]
        links += f'\n  <script defer src="/assets/{asset}?v={version}"></script>'
    return links


class Images(HTMLParser):
    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.sources = set()
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.sources.add(dict(attrs).get('src'))


REAL_LIFE_CASES = (
    ('/technology/checking-ai-website-changes/', 'AI-assisted website repair'),
    ('/technology/rightsreceipt-ai-licensing/', 'RightsReceipt licensing prototype'),
    ('/technology/local-ai-review-replies/', 'Review Reply Writer customer-reply case'),
    ('/technology/ai-book-continuity-checker/', 'Preflight manuscript continuity audit'),
    ('/technology/ai-poker-video-evidence/', 'AI-assisted poker-caption review'),
    ('/technology/dinner-on-time/', 'Dinner on Time cooking-planner simulation'),
)
CASE_INDEX_ID = 'real-life-case-index'
CASE_INDEX_NAME = 'Detailed practical AI case records'


def real_life_case_markup():
    links = '; '.join(f'<a href="{route}">{label}</a>'
                      for route, label in REAL_LIFE_CASES)
    return f'<p id="{CASE_INDEX_ID}"><strong>{CASE_INDEX_NAME}:</strong> {links}.</p>'


def real_life_case_schema(record, body, origin):
    """Only describe the six visible, reviewed case links on the portfolio."""
    canonical = origin + '/ai-in-real-life/'
    if (record.get('@type') != 'CollectionPage' or record.get('url') != canonical
            or 'mainEntity' in record):
        raise ValueError('Expected the canonical AI portfolio collection without an existing main entity')
    if (body.count(f'id="{CASE_INDEX_ID}"') != 1
            or body.count(real_life_case_markup()) != 1):
        raise ValueError('AI portfolio case index must match its six visible reviewed links')
    result = deepcopy(record)
    result['mainEntity'] = {
        '@type': 'ItemList', '@id': canonical + '#' + CASE_INDEX_ID,
        'name': CASE_INDEX_NAME, 'numberOfItems': len(REAL_LIFE_CASES),
        'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': label, 'url': origin + route}
            for i, (route, label) in enumerate(REAL_LIFE_CASES, 1)
        ],
    }
    return result


def schema(page, record, body, root, origin):
    if page['id'] == 'ai-in-real-life':
        return real_life_case_schema(record, body, origin)
    image = IMAGES.get(page['id'])
    if image is None:
        return record
    path, width, height, caption = image
    if record.get('@type') != 'Article':
        raise ValueError('Project image must describe a published article')
    if path not in Images(body).sources or not (root / path.lstrip('/')).is_file():
        raise ValueError('Project image must be present in the visible article')
    result = deepcopy(record)
    result['image'] = {
        '@type': 'ImageObject', 'url': origin + path,
        'width': width, 'height': height, 'caption': caption,
    }
    return result
