#!/usr/bin/env python3
"""Maintainer-only title-card rendering. Requires Pillow and installed DejaVu fonts."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
from PIL import Image, ImageDraw, ImageFont
import build
import reader_previews

ROOT = Path(__file__).resolve().parents[1]


def wrap(draw, title, font):
    lines = []
    for word in title.split():
        candidate = (lines[-1] + ' ' + word) if lines else word
        if not lines:
            lines.append(word)
        elif draw.textbbox((0, 0), candidate, font=font)[2] <= 1030:
            lines[-1] = candidate
        else:
            lines.append(word)
    return lines


def render(page, fonts):
    image = Image.new('RGB', (1200, 630), '#f1f3ed')
    draw = ImageDraw.Draw(image)
    draw.line((56, 48, 56, 580), fill='#b42332', width=3)
    tag = reader_previews.label(page)
    draw.text((94, 72), tag, font=ImageFont.truetype(fonts['regular'], 23), fill='#48534b')
    for size in range(64, 41, -2):
        font = ImageFont.truetype(fonts['bold'], size)
        lines = wrap(draw, page['title'], font)
        if len(lines) <= 3 and all(draw.textbbox((0, 0), line, font=font)[2] <= 1030 for line in lines):
            break
    else:
        raise ValueError('Title does not fit: ' + page['title'])
    line_height = size + 20
    top = 174 + (3 - len(lines)) * 20
    boxes = []
    for index, line in enumerate(lines):
        at = (94, top + index * line_height)
        box = draw.textbbox(at, line, font=font)
        if box[2] > 1124 or box[3] > 445:
            raise ValueError('Title exceeds safe area: ' + page['title'])
        boxes.append(box)
        draw.text(at, line, font=font, fill='#111b16')
    draw.line((94, 486, 1105, 486), fill='#b42332', width=2)
    draw.text((94, 526), 'Nolan Kido  /  nolankido.com', font=ImageFont.truetype(fonts['regular'], 27), fill='#48534b')
    bounds = [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]
    file = ROOT / ('assets/social/reader-' + page['id'] + '.png')
    image.quantize(colors=32).save(file, optimize=True)
    raw = file.read_bytes()
    if len(raw) >= 25_000:
        raise ValueError('Reader preview exceeds the existing delivery budget: ' + file.name)
    return {'path': page['path'], 'title': page['title'], 'label': tag,
            'src': '/' + file.relative_to(ROOT).as_posix(), 'sha256': sha256(raw).hexdigest(),
            'layout': {'lines': lines, 'font_size': size, 'bounds': bounds}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--regular', default='DejaVuSans.ttf')
    parser.add_argument('--bold', default='DejaVuSans-Bold.ttf')
    args = parser.parse_args()
    retained = set(json.loads((ROOT / '_source/presentation.json').read_text())['pages'])
    pages = [p for p in build.public_pages() if reader_previews.eligible(p) and p['id'] not in retained]
    records = {p['id']: render(p, {'regular': args.regular, 'bold': args.bold}) for p in pages}
    (ROOT / reader_previews.SOURCE).write_text(json.dumps({'version': 1, 'pages': records}, indent=2, ensure_ascii=False) + '\n')
    print('Rendered', len(records), 'reader previews; retained every existing card.')


if __name__ == '__main__':
    main()
