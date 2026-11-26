"""Cross-inventory search metadata and sitemap checks for registered books.

The book registry already validates each public HTML document against its
reviewed source. Here, compare those reviewed values with the generated-page
inventory and the committed sitemap. Keep historical audit counters intact.
"""
from collections import Counter, defaultdict
import unicodedata


def normalized(value):
    """Treat case, Unicode compatibility and whitespace variants as duplicates."""
    if not isinstance(value, str):
        return ''
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def discovery_errors(records, sitemap, generated_titles, generated_descriptions):
    """Return route-specific issues without modifying any inputs or snapshot.

    records contains only successfully validated standalone book/catalog rows:
    url, title, description, modified. The title/description iterables contain
    the metadata observed on generated public pages by the existing audit.
    """
    errors = []
    title_counts = Counter(normalized(value) for value in generated_titles)
    description_counts = Counter(normalized(value) for value in generated_descriptions)
    for record in records:
        title_counts[normalized(record['title'])] += 1
        description_counts[normalized(record['description'])] += 1

    locations = defaultdict(list)
    for entry in sitemap.findall('{*}url'):
        locs = entry.findall('{*}loc')
        for loc in locs:
            locations[loc.text].append((locs, entry.findall('{*}lastmod')))

    for record in records:
        url = record['url']
        title = normalized(record['title'])
        description = normalized(record['description'])
        if not title or title_counts[title] != 1:
            errors.append(url + ': book search title is empty or duplicates another page')
        if not description or description_counts[description] != 1:
            errors.append(url + ': book search description is empty or duplicates another page')
        rows = locations[url]
        if len(rows) != 1 or len(rows[0][0]) != 1:
            errors.append(url + ': book needs exactly one sitemap URL record')
        elif len(rows[0][1]) != 1 or rows[0][1][0].text != record['modified']:
            errors.append(url + ': book sitemap lastmod must match the reviewed revision date')
    return errors
