#!/usr/bin/env python3
"""Copy and validate exact standalone book source bytes. No GitHub Actions."""
import argparse
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import book_pages

ROOT = Path(__file__).resolve().parents[1]


def validate_staged(root: Path, reviewed: list[tuple[Path, Path, bytes]]) -> None:
    """Validate the exact candidate bytes and real inbound-link context before publishing."""
    with TemporaryDirectory(prefix='book-release-preflight-') as directory:
        stage = Path(directory)
        for source, target, data in reviewed:
            for relative in (source, target):
                path = stage / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        # These are the existing public inbound-link dependencies of the registry.
        for relative in ('index.html', 'creative/index.html', 'about/index.html', 'bio/index.html'):
            path = stage / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((root / relative).read_bytes())
        if book_pages.hub_record(stage) is None:
            raise ValueError('Books catalog is not staged')


def build(root: Path, *, check: bool = False) -> int:
    pairs = [(book_pages.HUB_SOURCE, book_pages.HUB_OUTPUT)]
    pairs.extend((Path('_source/books') / (item['slug'] + '.html'),
                  Path('books') / item['slug'] / 'index.html')
                 for item in book_pages.BOOKS)
    # Read and decode every source before any output can be overwritten.
    # Preserve source bytes, including line endings, rather than relying on
    # read_text()'s universal-newline conversion to certify exact parity.
    reviewed = []
    for source, target in pairs:
        try:
            data = (root / source).read_bytes()
            data.decode('utf-8')
        except (OSError, UnicodeError) as exc:
            print('Cannot read reviewed book source: ' + str(source) + ': ' + str(exc), file=sys.stderr)
            return 1
        reviewed.append((source, target, data))
    if not check:
        # Reuse the production registry instead of maintaining a second set of
        # SEO and identity rules. No public targets have been touched yet.
        validate_staged(root, reviewed)
    for _, relative, data in reviewed:
        target = root / relative
        if check:
            if not target.is_file() or target.read_bytes() != data:
                message = ('Books catalog differs from reviewed source' if relative == book_pages.HUB_OUTPUT
                           else 'Book page not in sync: ' + str(target))
                print(message, file=sys.stderr)
                return 1
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.is_file() or target.read_bytes() != data:
                target.write_bytes(data)
        print(('Checked ' if check else 'Built ') + str(relative))
    book_pages.published(root)
    if book_pages.hub_record(root) is None:
        print('Books catalog is not published', file=sys.stderr)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    return build(ROOT, check=parser.parse_args().check)


if __name__ == '__main__':
    raise SystemExit(main())
