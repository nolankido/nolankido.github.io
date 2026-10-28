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
})
SCOPED_IDS = CASE_IDS | {'home', 'technology', 'creative', 'ai-answer-review', 'ai-time-savings'}
IMAGES = {
    'ai-book-continuity-checker': (
        '/assets/projects/preflight-holmes-report.png', 1200, 1349,
        'Archived Preflight report showing source passages for possible Sherlock Holmes continuity errors.',
    ),
    'dinner-on-time': (
        '/assets/projects/dinner-on-time-preview.jpg', 2400, 1396,
        'The public Dinner on Time cooking-planner simulation demonstration.',
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
    return ''.join(
        '\n  <link rel="stylesheet" href="/assets/' + asset + '?v=' +
        sha256((root / 'assets' / asset).read_bytes()).hexdigest()[:12] + '">'
        for asset in assets
    )


class Images(HTMLParser):
    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.sources = set()
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.sources.add(dict(attrs).get('src'))


def schema(page, record, body, root, origin):
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
