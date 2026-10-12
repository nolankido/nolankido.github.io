"""Dates and locally hosted sharing cards. No runtime requests or publishing claims."""
from datetime import datetime
import html
import json
from pathlib import Path
import re
import struct
import reader_previews


def publication(page: dict) -> str:
    value = page.get('date')
    if not value:
        return ''
    when = datetime.strptime(value, '%Y-%m-%d')
    label = f"{when.strftime('%B')} {when.day}, {when.year}"
    return f'<p class="reading-date">Published <time datetime="{html.escape(value, quote=True)}">{label}</time></p>'


def load(root: Path, pages: list[dict]) -> dict:
    config = json.loads((root / '_source/presentation.json').read_text(encoding='utf-8'))
    if not isinstance(config, dict) or not isinstance(config.get('pages'), dict):
        raise ValueError('Presentation needs a default card and page overrides')
    config['pages'].update(reader_previews.load(root, pages, set(config['pages'])))
    ids = {p['id'] for p in pages}
    if not set(config['pages']).issubset(ids):
        raise ValueError('Sharing card must belong to a published page')
    for card in [config.get('default'), *config['pages'].values()]:
        if not isinstance(card, dict) or not isinstance(card.get('alt'), str) or not card['alt'].strip():
            raise ValueError('Sharing images need descriptive alternative text')
        src = card.get('src')
        if not isinstance(src, str) or not re.fullmatch(r'/assets/social/[a-z0-9-]+[.]png', src):
            raise ValueError('Sharing images must be local PNG assets')
        file = (root / src.lstrip('/')).resolve()
        if not file.is_relative_to(root.resolve()):
            raise ValueError('Sharing image escaped the site directory')
        raw = file.read_bytes()
        if len(raw) < 33 or len(raw) > 500_000 or raw[:16] != b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR':
            raise ValueError('Invalid or oversized sharing PNG')
        width, height = struct.unpack('>II', raw[16:24])
        if (width, height) != (1200, 630):
            raise ValueError('Sharing image must be 1200 by 630 pixels')
    return config


def metadata(config: dict, page: dict, origin: str) -> str:
    card = config['pages'].get(page['id'], config['default'])
    url = html.escape(origin + card['src'], quote=True)
    alt = html.escape(card['alt'], quote=True)
    return (f'<meta property="og:image" content="{url}">\n'
            '  <meta property="og:image:type" content="image/png">\n'
            '  <meta property="og:image:width" content="1200">\n'
            '  <meta property="og:image:height" content="630">\n'
            f'  <meta property="og:image:alt" content="{alt}">\n'
            '  <meta name="twitter:card" content="summary_large_image">\n'
            f'  <meta name="twitter:image" content="{url}">\n'
            f'  <meta name="twitter:image:alt" content="{alt}">')
