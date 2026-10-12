"""Fast HTML5 validation before browser tests; requires requirements-test.txt."""
from pathlib import Path
import json
import sys

import html5lib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build


def parse_errors(document: str) -> list:
    parser = html5lib.HTMLParser(strict=False)
    parser.parse(document)
    return parser.errors


def main() -> int:
    # Verify that the parser catches the exact class of release regression.
    good = '<!doctype html><html lang="en"><head><title>Check</title></head><body><section><div><p>Text</p></div></section></body></html>'
    bad = good.replace('</div></section>', '</div></div></section>')
    if parse_errors(good) or not parse_errors(bad):
        raise RuntimeError('HTML5 checker self-test failed')
    pages = build.public_pages()
    failures = []
    for page in pages:
        route = page['path']
        relative = route.lstrip('/') + ('index.html' if route.endswith('/') else '')
        errors = parse_errors((ROOT / relative).read_text(encoding='utf-8'))
        if errors:
            failures.append({'path': route, 'errors': errors})
    print(json.dumps({'status': 'fail' if failures else 'pass',
                      'pages': len(pages), 'self_test': 'pass',
                      'failures': failures}, indent=2))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
