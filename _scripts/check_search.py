#!/usr/bin/env python3
"""Audit committed search metadata, identity, breadcrumbs, and crawl policy.

No network or ranking claims. This checks the generated files a release serves,
not merely the source configuration. Run build.py --check separately for drift.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from xml.etree import ElementTree as ET
import build
import public_identity
from search_visibility import UTILITY_IDS, BreadcrumbLinks

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, content: str):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.title = ''
        self.h1 = ''
        self.schemas = []
        self.capture = None
        self.schema_text = ''
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if tag in {'title', 'h1'}:
            self.capture = tag
        elif tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.capture = 'schema'
            self.schema_text = ''

    def handle_data(self, data):
        if self.capture == 'schema':
            self.schema_text += data
        elif self.capture in {'title', 'h1'}:
            setattr(self, self.capture, getattr(self, self.capture) + data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.capture == 'schema':
            self.schemas.append(json.loads(self.schema_text))
            self.capture = None
        elif tag == self.capture:
            self.capture = None

    def tags(self, tag):
        return [attrs for name, attrs in self.elements if name == tag]


def audit(root: Path, pages: list[dict], origin: str) -> dict:
    errors = []
    titles = Counter()
    descriptions = Counter()
    totals = Counter()
    routes = {origin + page['path'] for page in pages}
    person_id = origin + '/about/#nolan-kido'
    expected_indexed = {origin + p['path'] for p in pages if not p.get('noindex')}
    sitemap = ET.fromstring((root/'sitemap.xml').read_text(encoding='utf-8'))
    actual_indexed = [e.text for e in sitemap.iter() if e.tag.endswith('}loc')]
    if set(actual_indexed) != expected_indexed or len(actual_indexed) != len(expected_indexed):
        errors.append('Sitemap must contain each indexable canonical exactly once')
    for page in pages:
        path = page['path']
        url = origin + path
        def check(condition, message):
            if not condition:
                errors.append(path + ': ' + message)
        try:
            content = (root/build.output_path(path)).read_text(encoding='utf-8')
            doc = Document(content)
            titles[doc.title] += 1
            check(doc.title == page['seo_title'], 'Search title disagrees with manifest')
            for tag in ['title', 'h1', 'main']:
                check(len(doc.tags(tag)) == 1, 'Need exactly one ' + tag)
            meta = doc.tags('meta')
            values = {a.get('name', a.get('property')): a.get('content') for a in meta}
            descriptions[values.get('description', '')] += 1
            check(values.get('description') == page['description'], 'Description disagrees with manifest')
            canonicals = [a.get('href') for a in doc.tags('link') if a.get('rel') == 'canonical']
            check(canonicals == [url], 'Need one canonical on the approved HTTPS host')
            check(values.get('og:url') == url, 'Share URL must match canonical')
            check(values.get('og:title') == doc.title, 'Share title must match search title')
            check(values.get('og:description') == values.get('description'), 'Share summary must match search summary')
            check(values.get('twitter:image') == values.get('og:image'), 'Sharing images must agree')
            noindex = 'noindex' in values.get('robots', '').lower().split(',')
            check(noindex == bool(page.get('noindex')), 'Robots directive disagrees with explicit crawl policy')
            check(bool(page.get('noindex')) == (page['id'] in UTILITY_IDS or page['id'] == '404'), 'Unexpected indexing exclusion')
            if noindex:
                totals['noindex_pages'] += 1
            check(len(doc.schemas) == 1, 'Need one connected structured-data document')
            if len(doc.schemas) != 1:
                continue
            schema = doc.schemas[0]
            check(schema.get('url') == url, 'Structured-data URL must match canonical')
            website = schema.get('isPartOf', {})
            check(website.get('@id') == origin + '/#website', 'WebSite identity must be stable')
            check(website.get('publisher', {}).get('@id') == person_id, 'WebSite publisher must identify Nolan')
            article = schema.get('@type') == 'Article'
            check(schema.get('@id') == url + ('#article' if article else '#webpage'), 'Entity ID must match page type')
            if article:
                totals['articles'] += 1
                author = schema.get('author', {})
                check(author.get('@id') == person_id and author.get('url') == origin + '/about/', 'Article author must resolve to profile')
                check(schema.get('datePublished') == page.get('date'), 'Do not reset article publication dates')
                check(schema.get('dateModified') == page.get('updated'), 'Revision date must be explicit')
                check(any(a.get('href') == '/about/' for a in doc.tags('a')), 'Authorship needs a visible profile link')
                check('Nolan Kido</a>' in content, 'Authorship needs a visible author name')
                webpage = schema.get('mainEntityOfPage', {})
                check(webpage.get('@type') == 'WebPage' and webpage.get('@id') == url + '#webpage', 'Article must identify a distinct containing WebPage')
            else:
                webpage = schema
            breadcrumb = webpage.get('breadcrumb')
            navs = [a for a in doc.tags('nav') if a.get('aria-label') == 'Breadcrumb']
            if page['id'] not in {'home', '404'}:
                check(len(navs) == 1, 'Need one visible breadcrumb, not duplicate navigation')
                check(bool(breadcrumb), 'Visible breadcrumb needs structured counterpart')
                if breadcrumb:
                    totals['breadcrumb_pages'] += 1
                    items = breadcrumb.get('itemListElement', [])
                    check(len(items) >= 2, 'Breadcrumb must contain a parent and current page')
                    check([i.get('position') for i in items] == list(range(1, len(items)+1)), 'Breadcrumb positions must be consecutive')
                    check(all(i.get('item') in routes and i.get('name') for i in items), 'Breadcrumbs must reference published pages with labels')
                    check(items[-1].get('item') == url, 'Breadcrumb must end at the current canonical')
                    visible = BreadcrumbLinks(content).links
                    actual = [(i['item'].removeprefix(origin), i['name']) for i in items[:-1]]
                    check(actual == visible, 'Structured breadcrumb parents must match visible links and labels')
            else:
                check(not breadcrumb and not navs, 'Home and 404 do not need artificial breadcrumbs')
            # Identity markup cannot turn aspirations into credentials or social proof.
            claim_schema = deepcopy(schema)
            if page['id'] in {'home', 'about'}:
                for role in ['about', 'mainEntity']:
                    person = claim_schema.get(role, {})
                    check(person.get('@type') == 'Person' and person.get('@id') == person_id,
                          'Public profile links must belong to the shared Person identity')
                    check(person.pop('sameAs', None) == public_identity.same_as(),
                          'Person sameAs must contain exactly the verified public-work profiles')
                if page['id'] == 'about':
                    visible_profiles = [a.get('href') for a in doc.tags('a')
                                        if 'me' in a.get('rel', '').split()]
                    check(visible_profiles == public_identity.same_as(),
                          'About must visibly link to the same verified public-work profiles')
            identity_json = json.dumps(claim_schema)
            for key in ['sameAs', 'award', 'aggregateRating', 'reviewRating', 'alumniOf', 'worksFor', 'hasCredential']:
                check('"' + key + '"' not in identity_json, 'Unsupported identity claim: ' + key)
            if page['id'] == 'about':
                check(schema.get('@type') == 'ProfilePage', 'About must remain the profile page')
                check(schema.get('mainEntity', {}).get('@id') == person_id, 'Profile must own the shared Person identity')
            if page['id'] == 'task-brief':
                app = schema.get('mainEntity', {})
                check(app.get('@type') == 'WebApplication' and app.get('isAccessibleForFree') is True, 'Describe the actual free browser application')
                check('No AI runs here.' in content, 'Keep the tool boundary visible')
            totals['pages'] += 1
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(path + ': ' + str(exc))
    for label, counts in [('titles', titles), ('descriptions', descriptions)]:
        if not all(value and count == 1 for value, count in counts.items()):
            errors.append('Empty or duplicated ' + label)
    return {'status': 'fail' if errors else 'pass', 'scope': 'committed static files, not rankings or indexing confirmation',
            **dict(totals), 'sitemap_urls': len(actual_indexed), 'unique_titles': len(titles),
            'unique_descriptions': len(descriptions), 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', type=Path, help='Optionally write the deterministic audit report')
    args = parser.parse_args()
    site = json.loads((ROOT/'_source/site.json').read_text(encoding='utf-8'))
    result = audit(ROOT, build.public_pages(), site['url'])
    rendered = json.dumps(result, indent=2) + '\n'
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding='utf-8')
    print(rendered, end='')
    return bool(result['errors'])


if __name__ == '__main__':
    sys.exit(main())
