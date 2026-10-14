"""Project visible section headings into the existing local search page.

Use generated public HTML, so labels and fragments match the published page.
Reuse the reading-outline parser to exclude disclosures and hidden answers.
No body prose, form values, remote content or excluded pages are indexed.
"""
import json
from pathlib import Path
import re
from poker_reading import VisibleHeadings
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


def index(outputs: dict[Path, str], pages: list[dict]) -> dict:
    result = {}
    for page in pages:
        if site_find.eligible(page):
            path = Path(page['path'].strip('/')) / 'index.html'
            result[page['path']] = headings(outputs[path])
    return result


def apply(outputs: dict[Path, str], pages: list[dict]) -> dict[Path, str]:
    document = outputs[PAGE]
    if BEGIN in document or document.count('</main>') != 1:
        raise ValueError('Add the search section index exactly once')
    # Flatten pairs on the wire to keep every heading inside the delivery budget.
    # The browser restores the exact [anchor, label] rows before filtering.
    packed = {path: [value for row in rows for value in row]
              for path, rows in index(outputs, pages).items()}
    data = json.dumps({'version': 2, 'pages': packed}, ensure_ascii=False, separators=(',', ':'))
    # JSON data is not executable script. Escape HTML delimiters defensively.
    for char, value in [('&', '\\u0026'), ('<', '\\u003c'), ('>', '\\u003e'),
                        ('\u2028', '\\u2028'), ('\u2029', '\\u2029')]:
        data = data.replace(char, value)
    block = BEGIN + '<script type="application/json" id="find-section-data">' + data + '</script>' + END + '\n'
    outputs[PAGE] = document.replace('</main>', block + '</main>', 1)
    return outputs
