"""One-time reviewed integration adjustments. Removed before the release is merged."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]


def replace(path, old, new):
    target = ROOT / path
    text = target.read_text(encoding='utf-8')
    if new in text:
        return
    if text.count(old) != 1:
        raise RuntimeError(f'Expected one reviewed integration anchor in {path}: {old[:70]}')
    target.write_text(text.replace(old, new, 1), encoding='utf-8')

# Publication and revision fields remain explicit and useful beyond the launch date.
for name in ('launch.json', 'further.json'):
    target = ROOT / '_source/living-well' / name
    data = json.loads(target.read_text())
    for entry in data['entries']:
        entry.setdefault('published', '2026-10-08')
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
replace('_scripts/living_well.py', "KINDS = {'essay': 'Essay', 'guide': 'Practical guide', 'experiment': 'Proposed experiment'}", "KINDS = {'essay': 'Essay', 'guide': 'Practical guide', 'experiment': 'Proposed experiment'}\n\ndef date_label(value: str) -> str:\n    date = datetime.strptime(value, '%Y-%m-%d')\n    return f'{date.strftime(\"%B\")} {date.day}, {date.year}'\n")
replace('_scripts/living_well.py', "        seen.add(slug)\n", "        seen.add(slug)\n        published = entry.get('published')\n        if not isinstance(published, str) or not re.fullmatch(r'\\d{4}-\\d{2}-\\d{2}', published):\n            raise ValueError('Living Well needs an explicit publication date: ' + slug)\n        date_label(published)\n        if entry.get('updated'):\n            date_label(entry['updated'])\n            if entry['updated'] < published:\n                raise ValueError('A Living Well revision cannot precede publication')\n        if entry.get('revision') and not entry.get('updated'):\n            raise ValueError('A Living Well revision needs an update date')\n")
replace('_scripts/living_well.py', "'living_well_entry': entry['slug'], 'date': DATE})", "'living_well_entry': entry['slug'], 'living_well_kind': entry['kind'], 'date': entry['published'],\n                      **{key: entry[key] for key in ('updated', 'revision') if entry.get(key)}})")
replace('_scripts/living_well.py', "    if page.get('living_well_topic'):\n        active = 'topics'", "    if page.get('living_well_topic'):\n        active = 'topics'\n    if page.get('living_well_kind'):\n        active = {'essay': 'ideas', 'guide': 'guides', 'experiment': 'field-notes'}[page['living_well_kind']]")
replace('_scripts/living_well.py', "'\">October 8, 2026</time></p>'", "'\">' + date_label(page['date']) + '</time></p>'")
replace('_scripts/living_well.py', "datetime.strptime(DATE, '%Y-%m-%d').replace(tzinfo=timezone.utc)", "datetime.strptime(entry['published'], '%Y-%m-%d').replace(tzinfo=timezone.utc)")
replace('_scripts/living_well.py', 'or print this page using your browser.', 'or open the previews you need and print this page using your browser.')
# The historical poker-only assertion should prohibit Poker navigation, not a different subsite.
replace('_tests/test_poker_finder.py', "            else:\n                self.assertNotIn('subsite-links', content)", "            elif p['path'].startswith('/living-well/'):\n                self.assertIn('aria-label=\"Living Well section\"', content)\n                nav = re.search(r'<nav class=\"subsite-links\".*?</nav>', content).group(0)\n                self.assertNotIn('href=\"/poker/find/\"', nav)\n                self.assertNotIn('href=\"/poker/resources/\"', nav)\n            else:\n                self.assertNotIn('subsite-links', content)")
# The permanent workflow stays read-only and retains all existing suites.
replace('.github/workflows/site-checks.yml', '          python _tests/design_browser.py\n', '          python _tests/design_browser.py\n          AXE_PATH="$RUNNER_TEMP/nk-qa/node_modules/axe-core/axe.min.js" python _tests/living_well_browser.py\n')
replace('.github/workflows/site-checks.yml', '            ${{ runner.temp }}/poker-reading-previews/*.log\n', '            ${{ runner.temp }}/poker-reading-previews/*.log\n            ${{ runner.temp }}/poker-reading-previews/living-well-*.png\n            ${{ runner.temp }}/poker-reading-previews/living-well-*.json\n')
subprocess.run([sys.executable, '_scripts/build.py'], cwd=ROOT, check=True)
# Review has approved only the new gateway, shared navigation, and hub stylesheet.
# Retain literal independent hashes for original Poker text, contact, privacy assets,
# original design, original feeds and catalog. Never refresh those automatically.
p = ROOT / '_tests/test_viewer_next.py'
text = p.read_text()
match = re.search(r'^PROTECTED=(\{.*\})$', text, re.M)
protected = ast.literal_eval(match.group(1))
allowed = {'index.html', 'technology/index.html', 'creative/index.html', 'assets/hubs.css'}
for path, previous in protected.items():
    actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    if path in allowed:
        protected[path] = actual
    elif actual != previous:
        raise RuntimeError('Protected original changed unexpectedly: ' + path)
text = text[:match.start(1)] + repr(protected) + text[match.end(1):]
text = text.replace('# October 7: the owner-requested viewer-questions refresh advances only its source hash.\n# Gateway, design, other guide and privacy protections remain unchanged.', '# October 8: owner-approved Living Well updates the gateway, shared navigation, and hubs CSS.\n# Original Poker source, contact code, design, site CSS, original feed and catalog hashes are retained.')
p.write_text(text)
p = ROOT / '_tests/test_poker_content.py'
text = p.read_text()
paths = ast.literal_eval(re.search(r'^BASELINE_PATHS = (\[.*\])$', text, re.M).group(1))
digest = hashlib.sha256()
for path in paths:
    digest.update(path.encode() + b'\0' + (ROOT / path).read_bytes() + b'\0')
text = re.sub(r"^BASELINE_DIGEST = '[a-f0-9]+'$", "BASELINE_DIGEST = '" + digest.hexdigest() + "'", text, flags=re.M)
text = text.replace('# October 6: approved Umami tag and privacy disclosure; other page bytes verified unchanged.', '# October 8: reviewed owner-approved Living Well gateway and shared navigation baseline; protected original source and contact assets retain separate fixed checks.')
p.write_text(text)
print('Reviewed gateway baseline:', digest.hexdigest())
