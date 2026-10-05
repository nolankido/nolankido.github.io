"""Regression checks for review fixes that must survive future content edits."""
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build

class ReviewTests(unittest.TestCase):
    def test_asset_versions_follow_content(self):
        outputs = build.build_outputs()
        css = hashlib.sha256((ROOT / 'assets/site.css').read_bytes()).hexdigest()[:12]
        js = hashlib.sha256((ROOT / 'assets/contact.js').read_bytes()).hexdigest()[:12]
        for path, content in outputs.items():
            if path.suffix == '.html':
                self.assertIn('/assets/site.css?v=ledger-20261005-' + css, content)
        self.assertIn('/assets/contact.js?v=' + js, outputs[Path('contact/index.html')])

    def test_recovery_instructions_exist_before_javascript(self):
        content = build.build_outputs()[Path('contact/index.html')]
        self.assertIn('id="contact-initialization"', content)
        self.assertIn('If the fields stay unavailable', content)
        self.assertIn('<noscript>', content)
        self.assertIn('<fieldset id="contact-fields" disabled>', content)
        self.assertIn('id="form-success"', content)

    def test_public_routes_stable(self):
        pages = json.loads((ROOT / '_source/pages.json').read_text())
        paths = {p['path'] for p in pages}
        for route in ['/', '/about/', '/contact/', '/resources/', '/notes/', '/bio/', '/card/', '/privacy/', '/404.html', '/notes/trustworthy-tools/', '/notes/decision-quality/', '/notes/learning-from-the-beginning/', '/notes/generous-explanations/', '/notes/finishing-is-a-decision/']:
            self.assertIn(route, paths)
        self.assertEqual((ROOT / 'CNAME').read_text().strip(), 'nolankido.com')

    def test_no_unexpected_form_destinations_or_message_storage(self):
        script = (ROOT / 'assets/contact.js').read_text()
        for value in ['localStorage', 'sessionStorage', 'console.log', 'sendBeacon']:
            self.assertNotIn(value, script)
        self.assertIn("redirect: 'error'", script)
        self.assertIn("failure.status >= 500", script)
        self.assertIn("typeof id !== 'string'", script)
        self.assertEqual(script.count('await fetch('), 1)
        config = json.loads((ROOT / '_source/site.json').read_text())
        self.assertEqual(config['form_action'], 'https://submit-form.com/uPlTgRTAR')

if __name__ == '__main__':
    unittest.main(verbosity=2)
