"""Idempotent source migration for the reviewed editorial design release."""
from pathlib import Path
import json
root = Path(__file__).resolve().parents[1]
path = root / '_scripts/build.py'
s = path.read_text(encoding='utf-8')
if 'from catalog import supplement' not in s:
    s = s.replace('from xml.etree import ElementTree as ET', 'from xml.etree import ElementTree as ET\n# Also supports importlib-based build checks.\nsys.path.insert(0, str(Path(__file__).resolve().parent))\nfrom catalog import supplement')
    s = s.replace("values['notes_list'] = notes_list", "values['notes_list'] = notes_list\n    values.update(supplement(ROOT, notes))")
    s = s.replace("['about', 'notes', 'contact']", "['about', 'notes', 'resources', 'contact']")
    path.write_text(s, encoding='utf-8')
path = root / '_source/pages.json'
pages = json.loads(path.read_text())
if not any(p['id'] == 'resources' for p in pages):
    pages.insert(3, {'id': 'resources', 'path': '/resources/', 'title': 'Put an idea to work.', 'seo_title': 'Resources | Nolan Kido', 'description': 'Editable worksheets for decision-making, checking tools, and learning. Read a preview or download a copy without an account.', 'kicker': 'Resources', 'source': 'resources.html'})
path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
path = root / '_source/privacy.html'
s = path.read_text()
if 'Typography' not in s:
    s = s.replace('<h2>Using the contact form</h2>', '<h2>Typography</h2>\n          <p>The site requests Schibsted Grotesk, Source Serif 4, and IBM Plex Mono from Google Fonts. Your browser contacts Google to retrieve the stylesheet and font files, which can disclose technical request information such as your IP address and browser details. The site remains readable with local fallback fonts when those requests are blocked. See the <a href="https://developers.google.com/fonts/faq/privacy">Google Fonts privacy information</a>.</p>\n          <h2>Using the contact form</h2>')
path.write_text(s, encoding='utf-8')
path = root / '_config.yml'
s = path.read_text()
if 'DESIGN_IMPLEMENTATION.md' not in s:
    s += '  - DESIGN_IMPLEMENTATION.md\n'
if 'optional_front_matter:' not in s:
    s += '\n# Keep editable Markdown worksheets as static downloads.\noptional_front_matter:\n  enabled: false\n'
path.write_text(s)
path = root / 'README.md'
s = path.read_text()
s = s.replace('The original `styles.css` remains the visual foundation. Functional additions and styles for new content are isolated in `assets/site.css`.', 'The approved editorial design is implemented in `styles.css`. State and accessibility rules are isolated in `assets/site.css`. The resource catalog is in `_scripts/catalog.py` and the downloadable worksheets are in `downloads/`. See `DESIGN_IMPLEMENTATION.md` for the design decisions.')
path.write_text(s)
path = root / '.github/workflows/site-checks.yml'
s = path.read_text()
s = s.replace('run: python _tests/browser.py', 'run: |\n          python _tests/browser.py\n          python _tests/design_browser.py')
path.write_text(s)
print('Editorial source migration applied; original contact behavior preserved.')
