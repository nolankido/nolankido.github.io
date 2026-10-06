"""Accessible naming regression for the Poker destination group."""
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build

class PokerAccessibilityTests(unittest.TestCase):
    def test_reader_paths_have_a_nameable_role(self):
        output = build.build_outputs()[Path('poker/index.html')]
        self.assertIn('class="poker-paths" role="group" aria-label="Ways to explore Poker"', output)

if __name__ == '__main__':
    unittest.main()
