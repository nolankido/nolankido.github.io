#!/usr/bin/env python3
"""Copy and validate standalone book pages. No GitHub Actions."""
import argparse
from pathlib import Path
import sys
import book_pages

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    check = parser.parse_args().check
    hub_source, hub_output = ROOT / book_pages.HUB_SOURCE, ROOT / book_pages.HUB_OUTPUT
    hub_html = hub_source.read_text(encoding="utf-8")
    if check:
        if not hub_output.is_file() or hub_output.read_text(encoding="utf-8") != hub_html:
            print("Books catalog differs from reviewed source", file=sys.stderr)
            return 1
    else:
        hub_output.parent.mkdir(parents=True, exist_ok=True)
        hub_output.write_text(hub_html, encoding="utf-8", newline="")
    print(("Checked " if check else "Built ") + str(book_pages.HUB_OUTPUT))
    for item in book_pages.BOOKS:
        source = ROOT / ("_source/books/" + item["slug"] + ".html")
        target = ROOT / ("books/" + item["slug"] + "/index.html")
        data = source.read_text(encoding="utf-8")
        if check:
            if not target.exists() or target.read_text(encoding="utf-8") != data:
                print("Book page not in sync: " + str(target), file=sys.stderr)
                return 1
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(data, encoding="utf-8", newline="")
        print(("Checked " if check else "Built ") + str(target.relative_to(ROOT)))
    book_pages.published(ROOT)
    if book_pages.hub_record(ROOT) is None:
        print('Books catalog is not published', file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
