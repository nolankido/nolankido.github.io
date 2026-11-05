"""Fast HTML5 validation before browser tests; requires requirements-test.txt."""
from pathlib import Path
import json
import sys

import html5lib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import player_sitemap
import poker_episode
import poker_standoff_episode
import local_laptop_case
import reply_audit_case


def parse_errors(document: str) -> list:
    parser = html5lib.HTMLParser(strict=False)
    parser.parse(document)
    return parser.errors


def publication_paths(root: Path, pages: list[dict]) -> dict[str, Path]:
    """Include every source-validated standalone page, without reading the network."""
    paths = {page['path']: build.output_path(page['path']) for page in pages}
    manual = (
        (player_sitemap, player_sitemap.ROUTE, player_sitemap.RELATIVE),
        (poker_episode, poker_episode.ROUTE, poker_episode.OUTPUT),
        (poker_standoff_episode, poker_standoff_episode.ROUTE, poker_standoff_episode.OUTPUT),
        (local_laptop_case, local_laptop_case.ROUTE, local_laptop_case.OUTPUT),
        (reply_audit_case, reply_audit_case.ROUTE, reply_audit_case.OUTPUT),
    )
    for registry, route, output in manual:
        if registry.record(root) is None:
            continue
        if route in paths:
            raise ValueError('Standalone HTML duplicates a manifest route: ' + route)
        paths[route] = output
    return paths


def main() -> int:
    # Verify that the parser catches the exact class of release regression.
    good = '<!doctype html><html lang="en"><head><title>Check</title></head><body><section><div><p>Text</p></div></section></body></html>'
    bad = good.replace('</div></section>', '</div></div></section>')
    if parse_errors(good) or not parse_errors(bad):
        raise RuntimeError('HTML5 checker self-test failed')
    pages = publication_paths(ROOT, build.public_pages())
    failures = []
    for route, relative in pages.items():
        errors = parse_errors((ROOT / relative).read_text(encoding='utf-8'))
        if errors:
            failures.append({'path': route, 'errors': errors})
    print(json.dumps({'status': 'fail' if failures else 'pass',
                      'pages': len(pages), 'self_test': 'pass',
                      'failures': failures}, indent=2))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
