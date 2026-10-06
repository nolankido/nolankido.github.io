#!/usr/bin/env python3
"""Apply the two small refinements found in the first release review."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    content = target.read_text(encoding='utf-8')
    if content.count(old) != 1:
        raise RuntimeError('Expected one reviewed anchor in ' + path)
    target.write_text(content.replace(old, new), encoding='utf-8', newline='')

replace('assets/hubs.css', '.home-connection p {', '.home-connection .section-content > p {')
replace('_source/poker/reviewing-a-hand.html', '<div class="fictional-hand" aria-labelledby="example-title">', '<div class="fictional-hand" role="group" aria-labelledby="example-title">')
replace('_tests/test_poker.py', "        self.assertIn('Use it after play.', text)", "        self.assertIn('Use it after play.', text)\n        self.assertIn('class=\"fictional-hand\" role=\"group\" aria-labelledby=\"example-title\"', text)")
print('Refined the gateway rail typography and explicitly named hand-example group. Rebuild and run every release check.')
