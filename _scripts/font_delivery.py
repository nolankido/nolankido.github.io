"""Serve reviewed, unmodified font files and declarations from the site itself.

Preserve the recorded provider CSS as provenance. Only its URLs are localized;
family, style, weight, display and Unicode coverage stay exact. Builds are offline.
"""
from hashlib import sha256
from html import unescape
from pathlib import Path
import json
import re

SOURCE = Path('_source/font-faces.css')
OUTPUT = Path('assets/site-fonts.css')
PROVENANCE = Path('_reports/font-css-provenance.json')
LOCAL_PROVENANCE = Path('_reports/local-fonts-provenance.json')
FILE_PRECONNECT = '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
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


def local_files(root: Path) -> list[dict]:
    """Require exact URL coverage, content-addressed files and bundled licenses."""
    source = declarations(root)
    expected = set(re.findall(r'url\(([^)]+)\)', source))
    record = json.loads((root / LOCAL_PROVENANCE).read_text(encoding='utf-8'))
    fonts, licenses = record['files'], record['licenses']
    if len(fonts) != len(expected) or {f['url'] for f in fonts} != expected:
        raise ValueError('Local fonts must cover every original provider URL exactly once')
    families = {url.split('/s/')[1].split('/')[0] for url in expected}
    if len(licenses) != len(families) or {f['path'] for f in licenses} != {
            'assets/fonts/' + family + '-OFL.txt' for family in families}:
        raise ValueError('Each font family needs its original license')
    for entry in fonts + licenses:
        path = entry['path']
        if entry in fonts:
            family = entry['url'].split('/s/')[1].split('/')[0]
            if path != 'assets/fonts/' + family + '-' + entry['sha256'][:12] + '.woff2':
                raise ValueError('Font path must identify its family and exact content')
        data = (root / path).read_bytes()
        if len(data) != entry['bytes'] or sha256(data).hexdigest() != entry['sha256']:
            raise ValueError('Font asset does not match the reviewed provider bytes: ' + path)
        if entry in fonts:
            if data[:4] != b'wOF2' or int.from_bytes(data[8:12], 'big') != len(data):
                raise ValueError('Invalid WOFF2 asset: ' + path)
        elif b'SIL OPEN FONT LICENSE' not in data or b'Copyright' not in data:
            raise ValueError('Missing font copyright and license: ' + path)
    return fonts + licenses


def local_declarations(root: Path) -> str:
    text = declarations(root)
    for entry in local_files(root):
        if entry['path'].endswith('.woff2'):
            text = text.replace('url(' + entry['url'] + ')', 'url(/' + entry['path'] + ')')
    return text


def apply(outputs: dict[Path, str], root: Path) -> dict[Path, str]:
    text = local_declarations(root)
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
        if document.count(FILE_PRECONNECT) != 1:
            raise ValueError('Unexpected font-file preconnection: ' + str(path))
        document = GOOGLE_LINK.sub(lambda m: link, document)
        document = document.replace('  ' + PRECONNECT + '\n', '')
        document = document.replace('  ' + FILE_PRECONNECT + '\n', '')
        outputs[path] = document
    outputs[OUTPUT] = text
    return outputs
