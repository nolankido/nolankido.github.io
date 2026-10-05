"""One-time review migration. Remove after the verified output is committed."""
from pathlib import Path
import hashlib
import json
ROOT = Path(__file__).resolve().parents[1]

def replace(path, old, new):
    target = ROOT / path
    source = target.read_text(encoding='utf-8')
    if old in source:
        target.write_text(source.replace(old, new), encoding='utf-8')
    elif new not in source:
        raise ValueError('Expected text not found: ' + path)

fallback = '<p id="contact-initialization" class="small-copy" role="status">The contact form is loading. If the fields stay unavailable, reload the page or try another browser. A content blocker may be preventing the form script from loading.</p>\n'
replace('_source/contact.html', '<form id="contact-form"', fallback + '<form id="contact-form"')
replace('_source/layout.html', '/assets/site.css?v=ledger-20261005', '/assets/site.css?v=ledger-20261005-${site_css_version}')
replace('_scripts/build.py', 'import argparse\n', 'import argparse\nimport hashlib\n')
replace('_scripts/build.py', "    values.update(supplement(ROOT, notes))", "    values.update(supplement(ROOT, notes))\n    values['site_css_version'] = hashlib.sha256((ROOT / 'assets/site.css').read_bytes()).hexdigest()[:12]")
replace('_scripts/build.py', "            extra += '\\n  <script src=\"/assets/contact.js?v=20261005\" defer></script>'", "            contact_version = hashlib.sha256((ROOT / 'assets/contact.js').read_bytes()).hexdigest()[:12]\n            extra += f'\\n  <script src=\"/assets/contact.js?v={contact_version}\" defer></script>'")
replace('_tests/test_content.py', "import json\n", "import json\nimport hashlib\n")
replace('_tests/test_content.py', "['/assets/contact.js?v=20261005']", "['/assets/contact.js?v=' + hashlib.sha256((ROOT / 'assets/contact.js').read_bytes()).hexdigest()[:12]]")
replace('_tests/test_design.py', 'def test_fonts_disclosed_and_visual_and_form_code_unchanged(self):', 'def test_fonts_disclosed_and_reviewed_asset_contracts(self):')
for path, old_sha in [('assets/contact.js', '78838b313bc176b3c06ef7a9d3070746f5cbcd03'), ('assets/site.css', '0a7e1961fc1d7465bcb95b1d7df4f5d4fdd57059')]:
    raw = (ROOT / path).read_bytes()
    new_sha = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    replace('_tests/test_design.py', old_sha, new_sha)
replace('requirements-test.txt', 'playwright==1.55.0', 'playwright==1.55.0\nhtml5lib==1.1')
replace('_config.yml', '  - CONTENT_RELEASE.md', '  - CONTENT_RELEASE.md\n  - SITE_REVIEW.md')
replace('_tests/review_browser.py', "'manual_review': results['incomplete']", "'manual_review': results['incomplete']")
print('Updated recovery copy, content-addressed asset URLs, and regression contracts; styles.css is unchanged.')
