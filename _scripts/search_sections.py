"""Project visible section headings into the existing local search page.

Use generated public HTML, so labels and fragments match the published page.
Reuse the reading-outline parser to exclude disclosures and hidden answers.
No body prose, form values, remote content or excluded pages are indexed.
"""
import json
from collections import Counter
from pathlib import Path
import re
from poker_reading import VisibleHeadings
import player_find
import site_find

PAGE = Path('find/index.html')
BEGIN = '<!-- Search section index: start -->'
END = '<!-- Search section index: end -->'


def headings(document: str) -> list[list[str]]:
    mains = re.findall(r'<main\b[^>]*>(.*?)</main>', document, re.S)
    if len(mains) != 1:
        raise ValueError('Search sections require exactly one public main region')
    result = VisibleHeadings(mains[0]).headings
    if len({anchor for anchor, _ in result}) != len(result):
        raise ValueError('Search section destinations must be unique')
    return [list(row) for row in result]


def index(outputs: dict[Path, str], pages: list[dict], root: Path | None = None) -> dict:
    """Include the same validated standalone pages as the native Find cards.

    The optional root keeps manifest-only historical and minimal fixtures
    independent of the current repository. Never scan arbitrary HTML files.
    """
    result = {}
    for page in pages:
        if site_find.eligible(page):
            path = Path(page['path'].strip('/')) / 'index.html'
            result[page['path']] = headings(outputs[path])
    if root is not None:
        manifest_routes = {page['path'] for page in pages}
        for item in player_find.add(root, []):
            route = item['path']
            if not re.fullmatch(r'/(?:[a-z0-9-]+/)+', route):
                raise ValueError('Standalone search sections require a canonical local route')
            path = Path(route.strip('/')) / 'index.html'
            if route in manifest_routes or route in result or path in outputs:
                raise ValueError('Standalone search sections must not overlap generated page ownership')
            result[route] = headings((root / path).read_text(encoding='utf-8'))
    return result


def apply(outputs: dict[Path, str], pages: list[dict], root: Path | None = None) -> dict[Path, str]:
    document = outputs[PAGE]
    if BEGIN in document or document.count('</main>') != 1:
        raise ValueError('Add the search section index exactly once')
    # Group routes and pool repeated labels. Every anchor and label survives
    # verbatim; the browser restores the canonical rows before filtering.
    canonical = index(outputs, pages, root)
    counts = Counter(label for rows in canonical.values() for _, label in rows)
    labels = sorted(label for label, count in counts.items() if count > 1 and len(label) > 8)
    references = {label: i for i, label in enumerate(labels)}
    packed = {}
    for path, rows in canonical.items():
        group = path.split('/')[1]
        suffix = path[len(group) + 2:] if group else ''
        packed.setdefault(group, {})[suffix] = [value for anchor, label in rows
            for value in (anchor, references.get(label, label))]
    data = json.dumps({'version': 4, 'labels': labels, 'pages': packed}, ensure_ascii=False, separators=(',', ':'))
    # JSON data is not executable script. Escape HTML delimiters defensively.
    for char, value in [('&', '\\u0026'), ('<', '\\u003c'), ('>', '\\u003e'),
                        ('\u2028', '\\u2028'), ('\u2029', '\\u2029')]:
        data = data.replace(char, value)
    block = BEGIN + '<script type="application/json" id="find-section-data">' + data + '</script>' + END + '\n'
    outputs[PAGE] = document.replace('</main>', block + '</main>', 1)
    return outputs
