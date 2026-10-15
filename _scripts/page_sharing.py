"""One canonical-link sharing component for public articles and the two AI tools."""
from hashlib import sha256
from html import escape
from pathlib import Path
import re
from urllib.parse import urlsplit

BEGIN = '<!-- Canonical page sharing: start -->'
END = '<!-- Canonical page sharing: end -->'
ASSETS = ('page-sharing.css', 'page-sharing.js')


def eligible(page: dict) -> bool:
    return not page.get('noindex') and bool(
        page.get('note') or page.get('poker_entry') or page.get('poker_guide') or page.get('poker_comic') or
        page.get('living_well_entry') or page.get('evidence_article') or
        page.get('worked_guide') or page['id'] in {'task-brief', 'ai-time-savings'})


def controls() -> str:
    return ('<div class="page-share-controls">'
            '<button type="button" class="button" data-copy-page hidden>Copy page link</button>'
            '<button type="button" class="button" data-share-page hidden>Share page</button>'
            '</div><p class="page-share-status" role="status" aria-live="polite" aria-atomic="true"></p>')


def decorate(body: str, page: dict, origin: str) -> str:
    if not eligible(page):
        return body
    if BEGIN in body or 'class="page-share-controls"' in body:
        raise ValueError('Page sharing must be added exactly once')
    parts = urlsplit(origin)
    if parts.scheme != 'https' or parts.netloc != 'nolankido.com' or parts.path or parts.query or parts.fragment:
        raise ValueError('Page sharing needs the public canonical origin')
    path = page['path']
    if not re.fullmatch(r'/(?:[a-z0-9-]+/)+', path):
        raise ValueError('Only public canonical article/tool routes are shareable')
    url = escape(origin + path, quote=True)
    if page.get('note'):
        # Enhance the existing disclosure; do not make a duplicate Notes footer.
        marker = '<details class="note-keep"><summary>Keep or share this essay</summary>'
        if body.count(marker) != 1:
            raise ValueError('The original Notes sharing disclosure needs review')
        return body.replace(marker, marker + BEGIN + controls() + END, 1)
    block = ('<div class="page-share-wrap"><details class="page-share">'
             '<summary>Keep or share this page</summary>'
             '<p>Pass along this page, or keep its permanent link in your notes. '
             'Share page, where supported, sends only the public title and link, not calculator entries or worksheet answers.</p>'
             + controls() + '<p class="page-share-address" tabindex="-1"><a href="' + url + '">' + url + '</a></p>'
             '<p class="small-copy">No sharing account is needed here. The link also works without JavaScript. '
             'For a reading copy, use your browser’s Print command or Save as PDF.</p></details>'
             '<p class="page-share-print-origin">Nolan Kido · Original page: <a href="' + url + '">' + url + '</a></p></div>')
    return body + BEGIN + block + END


def head(page: dict, root: Path) -> str:
    if not eligible(page):
        return ''
    extra = ''
    for name in ASSETS:
        version = sha256((root / 'assets' / name).read_bytes()).hexdigest()[:12]
        src = '/assets/' + name + '?v=' + version
        extra += ('\n  <link rel="stylesheet" href="' + src + '">' if name.endswith('.css')
                  else '\n  <script defer src="' + src + '"></script>')
    return extra
