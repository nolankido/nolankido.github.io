"""One-time staging migration. Removed from the production release after verification."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]

def replace(path, old, new):
    file = root / path
    source = file.read_text(encoding='utf-8')
    if old not in source:
        if new in source:
            return
        raise ValueError('Expected source not found in ' + path)
    file.write_text(source.replace(old, new), encoding='utf-8')

pages_path = root / '_source/pages.json'
pages = json.loads(pages_path.read_text())
changes = {
    'home': {'seo_title': 'Nolan Kido | Useful Things & Clear Ideas', 'description': 'Nolan Kido is an independent builder and writer. Worked explanations, practical resources, and reflections on technology, learning, and creative work.'},
    'about': {'title': 'A little about me.', 'description': 'Meet Nolan Kido: an independent builder and writer interested in useful tools, clear explanations, creative work, and life beyond projects.'},
    'notes': {'description': 'Worked examples and reflections on trust, decisions, learning, communication, and knowing when to finish. Selected writing by Nolan Kido.'},
    'resources': {'title': 'Use what helps.', 'description': 'Private-use worksheets for decisions, tool checks, and learning. Blank editable copies, completed fictional examples, and clear limits.'},
    'contact': {'description': 'Write to Nolan Kido with a shared interest, a different perspective, a collaboration idea, or a simple hello. No pitch required.'},
    'trustworthy-tools': {'description': 'Two calculations agree. Both are wrong. A small worked example of the difference between a convincing demonstration and independent evidence.', 'revision': 'Reworked around a checkable median-versus-mean example; added input boundaries, shared-assumption failures, and interpretation limits.'},
    'decision-quality': {'description': 'A fictional gathering, an uncertain forecast, and a $30 choice. Separate the calculation from the people and assumptions it leaves out.', 'revision': 'Added an explicit expected-cost example, the assumptions behind it, and a distinction between uncertain outcomes and avoidable omissions.'},
    'learning-from-the-beginning': {'description': 'A fractions example, a smaller-week option, and a learning loop that leaves most of the effort for practice rather than planning.', 'revision': 'Added a concrete fractions example, a smaller-week option, and clearer boundaries around the retrieval-practice research.'},
}
for page in pages:
    if page['id'] in changes:
        page.update(changes[page['id']])
        page['updated'] = '2026-10-05'
new_notes = [
    {'id': 'generous-explanations', 'path': '/notes/generous-explanations/', 'title': 'What makes an explanation feel generous.', 'seo_title': 'What Makes an Explanation Feel Generous | Nolan Kido', 'description': 'Two versions of the same instruction show how writing can save the reader effort without simplifying away what matters.', 'kicker': 'Creative work & communication', 'source': 'notes/generous-explanations.html', 'note': True, 'date': '2026-10-05'},
    {'id': 'finishing-is-a-decision', 'path': '/notes/finishing-is-a-decision/', 'title': 'Finishing is a decision.', 'seo_title': 'Finishing Is a Decision | Nolan Kido', 'description': 'Distinguish a necessary repair from another possible improvement, define done, and leave room for the rest of the day.', 'kicker': 'Making things & making room', 'source': 'notes/finishing-is-a-decision.html', 'note': True, 'date': '2026-10-05'},
]
for page in new_notes:
    if page['id'] not in {p['id'] for p in pages}:
        pages.append(page)
pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
replace('_source/layout.html', 'Personal site · October 2026', 'Notes · Tools · Conversation')
replace('_source/privacy.html', 'The form asks for your name, email address, a reason for contact, and your message. Additional context is optional.', 'The form requires your name, email address, and message. Topic and additional context are optional.')
replace('_source/resources.html', 'These resources may be copied and adapted for personal or professional use, without attribution being required. Do not imply an endorsement or validation.', 'Take a private copy and adapt the prompts to your situation. Do not treat a completed worksheet as certification or an endorsement.')
replace('_source/home.html', '<a href="/notes/trustworthy-tools/">A working tool is not the same as a trustworthy one.</a>', '<a href="${featured_note_url}">${featured_note_title}</a>')
replace('_source/home.html', '<p class="section-deck">Two calculations agree. Both are wrong. A small example of why a convincing demonstration is not the same as independent evidence.</p>', '<p class="section-deck">${featured_note_description}</p>')
replace('_source/home.html', '<a class="button" href="/notes/trustworthy-tools/">Read the example', '<a class="button" href="${featured_note_url}">Read the example')
replace('_tests/test_site.py', "self.assertEqual(len(links), 3)", "self.assertEqual(len(links), len(notes))")
replace('_tests/test_site.py', "{'name', 'email', 'reason', 'message'}", "{'name', 'email', 'message'}")
replace('_tests/browser.py', "self.assertEqual(page.locator('.note-entry').count(), 3)", "self.assertEqual(page.locator('.note-entry').count(), sum(bool(p.get('note')) for p in json.loads((ROOT / '_source/pages.json').read_text())))")
replace('_tests/design_browser.py', "name='Explore the notes'", "name='Start reading'")
extra_test = '''    def test_general_hello_needs_no_topic_or_context(self):
        self.contact(); self.verify()
        self.page.locator('#contact-name').fill('Example Visitor')
        self.page.locator('#contact-email').fill('visitor@example.com')
        self.page.locator('#contact-message').fill('A simple hello, used only in a mocked test.')
        self.page.locator('#contact-submit').click()
        expect(self.page.locator('#form-success')).to_be_visible()
        self.assertEqual(len(self.posts), 1)
        self.assertEqual(self.posts[0]['reason'], '')
        self.assertEqual(self.posts[0]['context'], '')

'''
replace('_tests/browser.py', '    def test_duplicate_submit_prevention(self):', extra_test + '    def test_duplicate_submit_prevention(self):')
readme = root / 'README.md'
current = readme.read_text()
if '## Editorial maintenance' not in current:
    readme.write_text(current + '\n## Editorial maintenance\n\nSee `EDITORIAL_GUIDE.md` for public-content boundaries, owner approval, revision handling, and a small manual review practice. `_source/selection.json` controls curated homepage links and reading order independently of RSS dates. Resource examples are in `_source/examples/`; the blank downloads are their single source of truth. Add a note to both the manifest and reading order. Do not commit private drafts.\n\nThe 2026-10-05 content revision preserves the visual stylesheets and contact JavaScript byte-for-byte. The contact topic is now optional; only name, email, and message are required. Keep existing URLs stable. No visitor analytics, newsletter, login, or new background automation is introduced.\n', encoding='utf-8')
config = root / '_config.yml'
current = config.read_text()
if '  - EDITORIAL_GUIDE.md' not in current:
    config.write_text(current + '\n  - EDITORIAL_GUIDE.md\n  - CONTENT_RELEASE.md\n', encoding='utf-8')
print('Public source, metadata, and current behavior contracts updated. Visual CSS and contact JS untouched.')
