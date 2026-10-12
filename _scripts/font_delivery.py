"""Serve the existing font-face declarations locally, not through blocking API CSS.

No font binaries are copied. Preserve family, style, weight, display and full
Unicode coverage from the recorded Google CSS response. Builds are offline.
"""
from hashlib import sha256
from html import unescape
from pathlib import Path
import json
import re

SOURCE = Path('_source/font-faces.css')
OUTPUT = Path('assets/site-fonts.css')
PROVENANCE = Path('_reports/font-css-provenance.json')
FAMILIES = {'IBM Plex Mono': {('normal', '400'), ('normal', '500')},
            'Schibsted Grotesk': {('normal', w) for w in ['400', '500', '600', '700', '750']},
            'Source Serif 4': {('normal', '400'), ('normal', '600'), ('italic', '400')}}
GOOGLE_LINK = re.compile(r'<link rel="stylesheet" href="(https://fonts[.]googleapis[.]com/css2[^"<>]+)">')
PRECONNECT = '<link rel="preconnect" href="https://fonts.googleapis.com">'


def declarations(root: Path) -> str:
    raw = (root / SOURCE).read_bytes()
    record = json.loads((root / PROVENANCE).read_text(encoding='utf-8'))
    if sha256(raw).hexdigest() != record['sha256'] or len(raw) != record['bytes']:
        raise ValueError('Font CSS does not match the reviewed provider capture')
    text = raw.decode('utf-8')
    bare = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    blocks = re.findall(r'@font-face\s*\{([^{}]+)\}', bare)
    if not blocks or re.sub(r'@font-face\s*\{[^{}]+\}', '', bare).strip():
        raise ValueError('Font source must contain only reviewed font-face declarations')
    seen = {family: set() for family in FAMILIES}
    for block in blocks:
        entries = [p.strip().split(':', 1) for p in block.strip().split(';') if p.strip()]
        if any(len(p) != 2 for p in entries):
            raise ValueError('Malformed font descriptor')
        props = {k.strip(): v.strip() for k, v in entries}
        if len(props) != len(entries) or set(props) != {'font-family', 'font-style', 'font-weight', 'font-display', 'src', 'unicode-range'}:
            raise ValueError('Unexpected or duplicated font descriptor')
        family = props['font-family'].strip("'")
        pair = (props['font-style'], props['font-weight'])
        if family not in FAMILIES or pair not in FAMILIES[family] or props['font-display'] != 'swap':
            raise ValueError('Unreviewed font family, weight, style or display policy')
        if not re.fullmatch(r"url\(https://fonts[.]gstatic[.]com/s/[a-z0-9]+/v\d+/[A-Za-z0-9_-]+[.]woff2\) format\('woff2'\)", props['src']):
            raise ValueError('Font files must remain WOFF2 on the existing Google provider')
        if not re.fullmatch(r'U\+[0-9A-F?]+(?:-[0-9A-F]+)?(?:, U\+[0-9A-F?]+(?:-[0-9A-F]+)?)*', props['unicode-range']):
            raise ValueError('Invalid font Unicode coverage')
        seen[family].add(pair)
    if seen != FAMILIES:
        raise ValueError('A requested font family, weight or style is missing')
    return text


def href(text: str) -> str:
    return '/' + OUTPUT.as_posix() + '?v=' + sha256(text.encode()).hexdigest()[:12]


def apply(outputs: dict[Path, str], root: Path) -> dict[Path, str]:
    text = declarations(root)
    record = json.loads((root / PROVENANCE).read_text(encoding='utf-8'))
    link = '<link rel="stylesheet" href="' + href(text) + '">'
    for path, document in list(outputs.items()):
        if path.suffix != '.html':
            continue
        matches = list(GOOGLE_LINK.finditer(document))
        if len(matches) != 1 or unescape(matches[0].group(1)) != record['url']:
            raise ValueError('Review the changed font request before replacing it: ' + str(path))
        if document.count(PRECONNECT) != 1:
            raise ValueError('Unexpected font API preconnection: ' + str(path))
        document = GOOGLE_LINK.sub(lambda m: link, document)
        document = document.replace('  ' + PRECONNECT + '\n', '')
        outputs[path] = document
    outputs[OUTPUT] = text
    return outputs
