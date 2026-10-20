"""Search identity and crawl policy, derived from published content only.

Keep existing editorial breadcrumbs, share one Person/WebSite identity, and do
not manufacture credentials, ratings, social profiles, dates, or search claims.
"""
from __future__ import annotations
from copy import deepcopy
import re
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit

# These are reader utilities, not additional search landing pages. Their links
# remain available and crawlers must be allowed to see the noindex directive.
UTILITY_IDS = frozenset({'find', 'poker-find', 'living-well-find', 'card'})
# The dated Poker finder is an existing RSS record. Keep its original identity
# and date for subscribers even though it is no longer a search landing page.
LEGACY_FEED_IDS = frozenset({'poker-find'})
LABELS = {'/': 'Home', '/about/': 'About Nolan', '/bio/': 'Short biography',
          '/technology/': 'Technology', '/creative/': 'Creative Work',
          '/notes/': 'Writing', '/resources/': 'Resources', '/contact/': 'Contact',
          '/privacy/': 'Privacy', '/start-here/': 'Start here', '/follow/': 'Follow writing'}


def apply_policy(pages: list[dict]) -> list[dict]:
    """Return a copy so indexing policy cannot mutate another content catalog."""
    result = deepcopy(pages)
    for page in result:
        if page['id'] in UTILITY_IDS:
            page['noindex'] = True
    return result


class BreadcrumbLinks(HTMLParser):
    """Read links in the existing visible Breadcrumb navigation, not body links."""
    def __init__(self, content: str):
        super().__init__(convert_charrefs=True)
        self.nav_depth = 0
        self.active = False
        self.href = None
        self.label = []
        self.links: list[tuple[str, str]] = []
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'nav':
            if self.nav_depth:
                self.nav_depth += 1
            elif attrs.get('aria-label') == 'Breadcrumb':
                self.nav_depth = 1
                self.active = True
        if self.nav_depth and tag == 'a':
            self.href = attrs.get('href')
            self.label = []

    def handle_data(self, data):
        if self.href is not None:
            self.label.append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self.href is not None:
            self.links.append((self.href, ' '.join(''.join(self.label).split())))
            self.href = None
        if tag == 'nav' and self.nav_depth:
            self.nav_depth -= 1


def breadcrumb(page: dict, pages: list[dict], header: str) -> tuple[str, list[tuple[str, str]]]:
    """Use the real editorial hierarchy; add native navigation where absent."""
    if page['id'] in {'home', '404'}:
        return header, []
    by_path = {p['path']: p for p in pages}
    parsed = BreadcrumbLinks(header)
    trail = []
    if parsed.active:
        for route, label in parsed.links:
            if route not in by_path:
                raise ValueError('Breadcrumb must reference a published canonical page: ' + str(route))
            if route != page['path'] and route not in {r for r, _ in trail}:
                trail.append((route, label))
    else:
        trail.append(('/', 'Home'))
        parts = page['path'].strip('/').split('/')
        for depth in range(1, len(parts)):
            route = '/' + '/'.join(parts[:depth]) + '/'
            if route in by_path:
                trail.append((route, LABELS.get(route, by_path[route]['title'])))
    trail.append((page['path'], LABELS.get(page['path'], page['title'])))
    if not parsed.active:
        links = ''.join('<li><a href="' + escape(route, quote=True) + '">' + escape(label) + '</a></li>'
                        for route, label in trail[:-1])
        links += '<li><span aria-current="page">' + escape(trail[-1][1]) + '</span></li>'
        header = '<nav class="search-breadcrumb shell" aria-label="Breadcrumb"><ol>' + links + '</ol></nav>\n' + header
    return header, trail


def decorate(page: dict, pages: list[dict], site: dict, schema: dict, header: str,
             presentation: dict) -> tuple[dict, str]:
    """Connect existing page types after their section-specific decoration."""
    origin = site['url']
    parts = urlsplit(origin)
    if parts.scheme != 'https' or not parts.netloc or parts.path or parts.query or parts.fragment:
        raise ValueError('Search identity needs the canonical HTTPS origin without a trailing slash')
    url = origin + page['path']
    result = deepcopy(schema)
    # The page catalog records calendar days, not an actual profile edit time.
    # Google's optional ProfilePage dateModified expects a DateTime. Omit a
    # day-only value rather than invent midnight or the current build time.
    # Preserve independently supplied timestamps and all other page types.
    if (result.get('@type') == 'ProfilePage'
            and isinstance(result.get('dateModified'), str)
            and re.fullmatch(r'\d{4}-\d{2}-\d{2}', result['dateModified'])):
        result.pop('dateModified')
    person = {'@type': 'Person', '@id': origin + '/about/#nolan-kido',
              'name': site['name'], 'url': origin + '/about/'}
    result['@id'] = url + '#webpage'
    result['inLanguage'] = 'en-US'
    result['isPartOf'] = {'@type': 'WebSite', '@id': origin + '/#website',
                          'name': site['name'], 'url': origin + '/',
                          'publisher': person}
    header, trail = breadcrumb(page, pages, header)
    if len(trail) > 1:
        result['breadcrumb'] = {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb',
            'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': label, 'item': origin + route}
                                for i, (route, label) in enumerate(trail, 1)]}
    if result.get('@type') == 'Article':
        result['@id'] = url + '#article'
        result['author'] = dict(person)
        result['publisher'] = dict(person)
        result['mainEntityOfPage'] = {'@type': 'WebPage', '@id': url + '#webpage', 'url': url}
        if 'breadcrumb' in result:
            result['mainEntityOfPage']['breadcrumb'] = result.pop('breadcrumb')
        # Sharing title cards are not article illustrations. Do not add image
        # markup until a genuinely representative content image is available.
        if not page.get('note'):
            byline = ('<p class="search-author">By <a href="/about/" rel="author">' + escape(site['name']) +
                      '</a> · <a href="/start-here/#reading-this-site">About this writing</a></p>')
            header = header.replace('</section>', byline + '</section>', 1)
    if page['id'] in {'technology', 'creative', 'resources', 'notes'}:
        result['@type'] = 'CollectionPage'
    if page['id'] == 'task-brief':
        result['mainEntity'] = {
            '@type': 'WebApplication', '@id': url + '#application',
            'name': 'AI Task Brief Builder', 'url': url,
            'description': 'A free browser tool that assembles a task brief from your words. No AI runs here.',
            'applicationCategory': 'ProductivityApplication', 'operatingSystem': 'Web browser',
            'isAccessibleForFree': True,
            'browserRequirements': 'JavaScript for the interactive builder; examples and the blank template also work without JavaScript.',
            'creator': dict(person)}
    return result, header
