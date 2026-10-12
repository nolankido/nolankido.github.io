#!/usr/bin/env python3
"""Convert the existing SVG mark into PNG fallbacks; no new identity artwork."""
from pathlib import Path
import cairosvg
ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    original = (ROOT / 'favicon.svg').read_bytes()
    for name, size in [('favicon.png', 96), ('apple-touch-icon.png', 180)]:
        cairosvg.svg2png(bytestring=original, write_to=str(ROOT / name),
                        output_width=size, output_height=size)
        print(name, size, (ROOT / name).stat().st_size)
