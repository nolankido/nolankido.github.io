#!/usr/bin/env python3
"""Optional maintainer tool: render the static sharing cards (Pillow required).

Uses installed DejaVu fonts by default. No fonts are bundled. Supply paths to
installed fonts when needed. Review the rendered PNGs after changes; the site serves the
committed images and never invokes Pillow or a third-party image service.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PAPER = '#f1f3ed'
INK = '#111b16'
MUTED = '#48534b'
ACCENT = '#b42332'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--regular', default='DejaVuSans.ttf')
    parser.add_argument('--bold', default='DejaVuSans-Bold.ttf')
    parser.add_argument('--serif', default='DejaVuSerif.ttf')
    parser.add_argument('--only', nargs='+', choices=['nolan-kido', 'keep-the-judgment', 'practical-ai', 'task-brief'], help='Render selected cards without changing other approved images')
    args = parser.parse_args()
    fonts = {'regular': args.regular, 'bold': args.bold, 'serif': args.serif}
    out = ROOT / 'assets/social'; out.mkdir(parents=True, exist_ok=True)
    for name in (args.only or ['nolan-kido', 'keep-the-judgment', 'practical-ai', 'task-brief']):
        image = Image.new('RGB', (1200, 630), PAPER)
        draw = ImageDraw.Draw(image)
        draw.line((56, 48, 56, 580), fill=ACCENT, width=3)
        def text(x, y, value, size, family='regular', color=INK):
            font = ImageFont.truetype(fonts[family], size)
            bounds = draw.textbbox((x, y), value, font=font)
            if bounds[2] > 1144 or bounds[3] > 580:
                raise ValueError('Text exceeds sharing-card safe area: ' + value)
            draw.text((x, y), value, font=font, fill=color)
        if name == 'nolan-kido':
            text(94, 70, 'Nolan Kido', 86, 'bold')
            draw.line((94, 196, 1105, 196), fill=ACCENT, width=2)
            text(94, 248, 'Build useful things.', 54, 'serif')
            text(94, 328, 'Make room for a good life.', 54, 'serif')
            text(94, 524, 'nolankido.com', 28, color=MUTED)
        elif name == 'keep-the-judgment':
            text(94, 72, 'AN ESSAY / PRACTICAL AI', 23, color=MUTED)
            text(94, 190, 'Let AI do more.', 78, 'bold')
            text(94, 296, 'Keep the judgment.', 78, 'bold')
            draw.line((94, 450, 1105, 450), fill=ACCENT, width=2)
            text(94, 519, 'Nolan Kido  /  nolankido.com', 27, color=MUTED)
        elif name == 'practical-ai':
            text(94, 72, 'NOLAN KIDO / TECHNOLOGY', 23, color=MUTED)
            text(94, 180, 'Practical AI.', 78, 'bold')
            text(94, 286, 'For real life.', 78, 'bold')
            text(94, 420, 'Useful tools. Clear checks. Your judgment.', 31, 'serif')
            text(94, 528, 'nolankido.com/technology', 26, color=MUTED)
        else:
            text(94, 72, 'A FREE TOOL / NOLAN KIDO', 23, color=MUTED)
            text(94, 178, 'A clearer AI', 78, 'bold')
            text(94, 284, 'task brief.', 78, 'bold')
            text(94, 419, 'Purpose. Inputs. Output. Checks. Boundaries.', 30, 'serif')
            text(94, 528, 'nolankido.com/technology/task-brief', 26, color=MUTED)
        image = image.quantize(colors=32)
        image.save(out / (name + '.png'), optimize=True)
        print(name, (out / (name + '.png')).stat().st_size)


if __name__ == '__main__':
    main()
