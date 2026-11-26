"""Inspect generated-page metadata without losing conflicting crawl directives."""
from collections import defaultdict
import re

SINGLETONS = frozenset({'description', 'og:url', 'og:title', 'og:description',
                        'og:image', 'twitter:image', 'twitter:title',
                        'twitter:description'})


def crawler_field(name):
    return name == 'robots' or bool(re.fullmatch(r'[a-z0-9_-]*bot(?:-[a-z0-9_-]+)?', name))


def directives(value):
    # Preserve colon-qualified values such as max-image-preview: none.
    return set(re.split(r'[,\s]+', re.sub(r'\s*:\s*', ':', value.lower())))


def inspect_metadata(meta, *, expected_noindex):
    """Return normalized values, the explicit global noindex flag, and errors.

    Indexable pages must not contain global or crawler-specific noindex/none.
    Utility pages must retain a global noindex, not just a bot-specific rule.
    The counters in the existing audit still count explicit global noindex.
    """
    fields = defaultdict(list)
    for attrs in meta:
        for attribute in ('name', 'property'):
            name = (attrs.get(attribute) or '').strip().lower()
            if name:
                fields[name].append(attrs.get('content') or '')
    errors = []
    for name, values in sorted(fields.items()):
        if len(values) > 1 and (name in SINGLETONS or crawler_field(name)):
            errors.append('Duplicate search metadata (' + name + ')')
    global_noindex = any('noindex' in directives(v) for v in fields['robots'])
    blocking = sorted(name for name, values in fields.items() if crawler_field(name)
                      and any(directives(value) & {'noindex', 'none'} for value in values))
    if expected_noindex and not global_noindex:
        errors.append('Robots directive disagrees with explicit crawl policy')
    elif not expected_noindex and blocking:
        errors.append('Robots directive disagrees with explicit crawl policy (' + ', '.join(blocking) + ')')
    return {name: values[-1] for name, values in fields.items() if values}, global_noindex, errors
