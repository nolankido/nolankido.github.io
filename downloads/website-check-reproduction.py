"""Offline HTML5 regression demonstration and optional one-file check.

Requires html5lib==1.1, installed separately by the reader.

    python website-check-reproduction.py
    python website-check-reproduction.py --file path/to/built/index.html

The default uses two embedded teaching fixtures. Neither mode makes network
requests or writes files. The fixtures are not the complete historical page.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

try:
    import html5lib
except ImportError:
    sys.exit("Install the parser first: python -m pip install html5lib==1.1")


GOOD = ('<!doctype html><html lang="en"><head><title>Example</title></head>'
        '<body><section><div><p>Example only</p></div></section></body></html>')
BAD = GOOD.replace('</div></section>', '</div></div></section>')
EXPECTED_CODE = 'end-tag-too-early'
EXPECTED_TAG = 'div'


def errors(document: str) -> list[dict]:
    """Keep the HTML5 parser's precise error code and tag, not just a count."""
    parser = html5lib.HTMLParser(strict=False)
    parser.parse(document)
    return [
        {'line': position[0], 'column': position[1], 'code': code, 'details': data}
        for position, code, data in parser.errors
    ]


def expected_failure(items: list[dict]) -> bool:
    return any(item['code'] == EXPECTED_CODE and
               item['details'].get('name') == EXPECTED_TAG for item in items)


def demonstration() -> int:
    before, after = errors(BAD), errors(GOOD)
    passed = expected_failure(before) and not after
    print(json.dumps({
        'mode': 'reduced-fixture',
        'scope': 'Illustrative HTML fragments; not the original full-page audit',
        'expected_error': {'code': EXPECTED_CODE, 'tag': EXPECTED_TAG},
        'before': before,
        'after': after,
        'status': 'pass' if passed else 'fail',
    }, indent=2))
    return 0 if passed else 1


def inspect_file(path: Path) -> int:
    try:
        document = path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        print(json.dumps({'mode': 'local-file', 'path': str(path),
                          'status': 'read-error', 'error': str(exc)}, indent=2))
        return 2
    found = errors(document)
    print(json.dumps({
        'mode': 'local-file',
        'path': str(path),
        'scope': 'One local HTML5 parse; not a complete site or browser check',
        'status': 'pass' if not found else 'fail',
        'errors': found,
    }, indent=2))
    return 0 if not found else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', type=Path, help='Check one local built HTML file')
    args = parser.parse_args(argv)
    return inspect_file(args.file) if args.file is not None else demonstration()


if __name__ == '__main__':
    raise SystemExit(main())
