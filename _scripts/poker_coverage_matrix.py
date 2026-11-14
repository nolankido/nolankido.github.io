#!/usr/bin/env python3
"""Rebuild or verify the public Poker source-coverage snapshot.

This is a local, deterministic source-inventory check. It makes no network
requests, endorses no outside sources and does not infer article quality.
"""

from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
from itertools import combinations
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / '_reports/poker-authority/turn-01-coverage-matrix.md'


class FinderCards(HTMLParser):
    """Read generated native Finder cards without executing search JavaScript."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.cards: dict[str, list[dict]] = {}
        self.active: dict | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == 'article' and 'data-finder-card' in attributes:
            if self.active is not None:
                raise ValueError('Nested Finder cards')
            kind = attributes.get('data-kind', '')
            self.active = {'id': attributes.get('data-id'), 'href': ''}
            self.cards.setdefault(kind, []).append(self.active)
        elif tag == 'a' and self.active is not None and not self.active['href']:
            self.active['href'] = attributes.get('href', '')

    def handle_endtag(self, tag: str) -> None:
        if tag == 'article' and self.active is not None:
            self.active = None


def entries(root: Path, name: str) -> list[dict]:
    path = root / '_source/poker' / f'{name}.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    if set(data) != {'version', 'entries'} or data['version'] != 1 or not isinstance(data['entries'], list):
        raise ValueError(f'Unexpected Poker catalogue schema: {name}')
    return data['entries']


def inventory(root: Path = ROOT) -> dict:
    guides = entries(root, 'library')
    topics = entries(root, 'topics')
    resources = entries(root, 'resources')
    collections = entries(root, 'collections')
    guide_ids = [guide['slug'] for guide in guides]
    resource_ids = [resource['id'] for resource in resources]
    topic_ids = [topic['id'] for topic in topics]
    collection_ids = [collection['id'] for collection in collections]
    for label, ids in (('guide', guide_ids), ('resource', resource_ids),
                       ('topic', topic_ids), ('collection', collection_ids)):
        if len(ids) != len(set(ids)):
            raise ValueError(f'Duplicate Poker {label} identifier')

    known_guides = set(guide_ids)
    known_resources = set(resource_ids)
    known_categories = {resource['category'] for resource in resources}
    primary: dict[str, str] = {}
    secondary: dict[str, list[str]] = {slug: [] for slug in guide_ids}
    source_membership = Counter()
    topical_sources: dict[str, set[str]] = {}
    for topic in topics:
        ident = topic['id']
        main = topic['primary_guides']
        related = topic['related_guides']
        if len(main + related) != len(set(main + related)) or not set(main + related) <= known_guides:
            raise ValueError(f'Invalid guide membership in {ident}')
        if not set(topic['resource_categories']) <= known_categories:
            raise ValueError(f'Unknown resource category in {ident}')
        if not set(topic['resource_ids'] + topic['featured_resources']) <= known_resources:
            raise ValueError(f'Unknown resource ID in {ident}')
        for slug in main:
            if slug in primary:
                raise ValueError(f'Guide has two primary topics: {slug}')
            primary[slug] = ident
        for slug in related:
            secondary[slug].append(ident)
        selected = {item['id'] for item in resources if item['category'] in topic['resource_categories']}
        selected.update(topic['resource_ids'])
        if not set(topic['featured_resources']) <= selected:
            raise ValueError(f'Featured resource is outside topic: {ident}')
        topical_sources[ident] = selected
        source_membership.update(selected)

    if set(primary) != known_guides:
        raise ValueError(f'Guides without a primary topic: {sorted(known_guides - set(primary))}')
    if set(source_membership) != known_resources:
        raise ValueError(f'External sources without a topic: {sorted(known_resources - set(source_membership))}')
    for collection in collections:
        if not set(collection['resource_ids']) <= known_resources:
            raise ValueError(f'Unknown collection resource: {collection["id"]}')

    finder = FinderCards()
    finder.feed((root / 'poker/find/index.html').read_text(encoding='utf-8'))
    indexed_guides = {card['href'] for card in finder.cards.get('guide', [])}
    missing_guides = {f'/poker/{slug}/' for slug in guide_ids} - indexed_guides
    indexed_sources = {card['id'] for card in finder.cards.get('resource', [])}
    missing_sources = {f'external-{ident}' for ident in resource_ids} - indexed_sources
    if missing_guides or missing_sources:
        raise ValueError(f'Generated Poker Finder omissions: guides={sorted(missing_guides)}, '
                         f'resources={sorted(missing_sources)}')

    shared = []
    for a, b in combinations(topics, 2):
        a_guides = set(a['primary_guides'] + a['related_guides'])
        b_guides = set(b['primary_guides'] + b['related_guides'])
        overlap = sorted(a_guides & b_guides)
        if overlap:
            shared.append((len(overlap), a['id'], b['id'], overlap))
    shared.sort(key=lambda row: (-row[0], row[1], row[2]))
    return {'guides': guides, 'topics': topics, 'resources': resources,
            'collections': collections, 'primary': primary, 'secondary': secondary,
            'topical_sources': topical_sources, 'source_membership': source_membership,
            'shared': shared, 'finder': finder.cards}


def page(slug: str) -> str:
    return f'[/{slug}/](https://nolankido.com/poker/{slug}/)'


def hub(ident: str) -> str:
    return f'[{ident}](https://nolankido.com/poker/topics/{ident}/)'


def render(data: dict) -> str:
    guides = data['guides']
    topics = data['topics']
    resources = data['resources']
    collections = data['collections']
    primary = data['primary']
    secondary = data['secondary']
    sources = data['topical_sources']
    membership = data['source_membership']
    with_secondary = sum(bool(v) for v in secondary.values())
    multi_source = sum(count > 1 for count in membership.values())
    finder = data['finder']
    lines = [
        '# Poker authority: Turn 01 source coverage and overlap matrix',
        '',
        '> Generated from the four versioned Poker manifests by '
        '`python _scripts/poker_coverage_matrix.py --write`. '
        'The companion [editorial review](turn-01-editorial-priorities.md) '
        'records the separately performed live-route spot checks, reader questions and priorities.',
        '',
        '## Verified source-inventory totals',
        '',
        f'- **{len(guides)} original guides** in the library, each with exactly one primary hub.',
        f'- **{len(topics)} topic hubs** with derived guide and external-source memberships.',
        f'- **{len(resources)} reviewed external-resource records**, each mapped to at least one topic. '
        'Stored review metadata is not a fresh link recheck.',
        f'- **{len(collections)} curated resource collections**. Collections are filtered views, '
        'not additional unique resources.',
        f'- **{with_secondary} guides** have at least one secondary topic placement; '
        f'**{multi_source} sources** belong to more than one topic. '
        'Overlapping topic counts must not be summed.',
        f'- **Poker Finder** contains all {len(guides)} library guide destinations '
        f'and {len(resources)} external-resource records, within '
        f'{len(finder.get("guide", []))} on-site guide/page cards, '
        f'{len(finder.get("resource", []))} source cards and '
        f'{len(finder.get("glossary", []))} glossary cards. '
        'Finder guide/page cards are not a second original-guide count.',
        '',
        '## Topic-hub coverage',
        '',
        '| Hub | Primary guides | Related guides | Unique guides | External sources | Starter guide slugs |',
        '| --- | ---: | ---: | ---: | ---: | --- |',
    ]
    for topic in topics:
        main = topic['primary_guides']
        related = topic['related_guides']
        starts = ', '.join(f'`{step["guide"]}`' for step in topic['steps'])
        lines.append(f'| {hub(topic["id"])} | {len(main)} | {len(related)} | '
                     f'{len(main) + len(related)} | {len(sources[topic["id"]])} | {starts} |')

    lines.extend(['', '## All original guides, their primary home and secondary routes', '',
                  'A secondary topic placement is an intentional navigation overlap, '
                  'not evidence of duplicate article prose.', '',
                  '| Original guide | Library category | Primary hub | Other hubs | Reader level |',
                  '| --- | --- | --- | --- | --- |'])
    for guide in guides:
        slug = guide['slug']
        related = ', '.join(hub(s) for s in secondary[slug]) or 'None'
        lines.append(f'| {page(slug)} | {guide["topic"]} | {hub(primary[slug])} | '
                     f'{related} | {guide["level"]} |')

    lines.extend(['', '## Resource category inventory', '',
                  'Category counts are exclusive. Topic source counts above can overlap '
                  'because hubs select full categories and explicit resource IDs.', '',
                  '| External directory category | Unique resources |',
                  '| --- | ---: |'])
    by_category = Counter(resource['category'] for resource in resources)
    for category in sorted(by_category):
        lines.append(f'| `{category}` | {by_category[category]} |')

    lines.extend(['', '## Structural overlap between hubs', '',
                  'Shared guides are listed to help future editors distinguish a cross-link '
                  'from a new, standalone article need. No textual-similarity or duplication '
                  'judgment is made by this calculation.', '',
                  '| Hub pair | Shared guides | Slugs |', '| --- | ---: | --- |'])
    for count, a, b, slugs in data['shared']:
        lines.append(f'| {hub(a)} + {hub(b)} | {count} | '
                     + ', '.join(f'`{slug}`' for slug in slugs) + ' |')
    if not data['shared']:
        lines.append('| None | 0 | None |')

    lines.extend(['', '## Curated resource collections', '',
                  '| Collection | Included resource IDs |', '| --- | ---: |'])
    for collection in collections:
        lines.append(f'| `{collection["id"]}` | {len(collection["resource_ids"])} |')
    lines.extend(['', '## Limits and repeatability', '',
                  '- This is a **manifest-level coverage matrix**, not a ranking report, '
                  'traffic report, content-quality assessment, or validation of every '
                  'article statement.',
                  '- A hub source count means that a directory entry has a topic '
                  'membership. It does not mean Nolan has authored a dedicated '
                  'guide for each source or that its destination is currently reachable.',
                  '- `--check` fails if the checked-in matrix no longer matches source. '
                  'After a reviewed catalog change, rebuild the site, rerun '
                  '`--write`, inspect its diff '
                  'and update the editorial priorities if the relevant gaps change.',
                  '- The site build and internal-link checker remain the authority for '
                  'generated route and fragment correctness.', ''])
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--write', action='store_true', help='regenerate checked-in Markdown from source')
    actions.add_argument('--check', action='store_true', help='verify checked-in Markdown matches source')
    args = parser.parse_args()
    expected = render(inventory())
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(expected, encoding='utf-8')
        print(f'Wrote {REPORT.relative_to(ROOT)}')
        return 0
    if not REPORT.exists() or REPORT.read_text(encoding='utf-8') != expected:
        print('Poker coverage matrix is missing or stale. Review source and run --write.')
        return 1
    print('Poker coverage matrix matches the current source manifests.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
