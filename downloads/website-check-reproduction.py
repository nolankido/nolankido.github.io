"""Reduced reproduction of an extra HTML closing tag, not the full site.
Run: python -m pip install html5lib==1.1
Then: python website-check-reproduction.py
Only parses two embedded strings. No network or file writes in this script.
"""
import json
import sys
try:
    import html5lib
except ImportError:
    sys.exit("Install the parser first: python -m pip install html5lib==1.1")
GOOD = '<!doctype html><html lang="en"><head><title>Example</title></head><body><section><div><p>Example only</p></div></section></body></html>'
BAD = GOOD.replace('</div></section>', '</div></div></section>')

def errors(document):
    parser = html5lib.HTMLParser(strict=False)
    parser.parse(document)
    return parser.errors

def main():
    before, after = errors(BAD), errors(GOOD)
    print(json.dumps({"scope": "Reduced example, not a replay of the original site audit", "before": before, "after": after}, indent=2))
    if not before or after:
        return 1
    print("PASS: the reduced invalid fixture is detected; the repaired fixture parses without errors.")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
