"""The first homepage evidence path remains scoped, sourced and understandable."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build
import check_live
from reviewed_release import read as reviewed_bytes
import turn38_home_proof_history as history

PARENT = history.PARENT
RELEASE = "778c36ce5fe2d5b56397384e2fcf5dc1c0739fd8"
PROOF = re.compile(
    r'<section class="section folio-row identity-selection home-proof" '
    r'aria-labelledby="home-proof-title">.*?</section>', re.S)
LINKS = [
    "https://onlinelibrary.wiley.com/doi/10.1111/j.1475-679X.2012.00447.x",
    "/technology/review-reply-evidence-audit/",
    "/poker/nolan-kido/",
]


def errors(content: str) -> list[str]:
    found = PROOF.findall(content)
    if len(found) != 1:
        return ["missing or duplicate proof section"]
    block = found[0]
    problems = []
    if content.index('class="link-row identity-actions"') > content.index(block):
        problems.append("proof displaces primary introduction")
    if content.index(block) > content.index('id="visibility-projects-title"'):
        problems.append("proof appears after project gallery")
    if block.count('class="identity-reading"') != 3:
        problems.append("proof is not exactly three sources")
    if re.findall(r'<h3><a href="([^"]+)"', block) != LINKS:
        problems.append("unexpected evidence links")
    for item in (
        'aria-labelledby="home-proof-title"', '<h2 class="section-title" id="home-proof-title">',
        'accounting scholarship, not evidence that my AI projects work',
        'not measured client outcomes or a general error rate',
        'Gross cashes are not profit',
        'href="/about/#about-evidence-title"',
    ):
        if item not in block:
            problems.append("missing label, context, or caveat: " + item)
    if '\u2014' in block or '<script' in block or 'onclick=' in block:
        problems.append("unexpected scripts or editorial punctuation")
    return problems


class HomepageEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '_source/home.html').read_text(encoding='utf-8')
        cls.page = (ROOT / 'index.html').read_text(encoding='utf-8')

    def test_three_distinct_claims_have_caveats_and_descriptive_links(self):
        self.assertEqual(errors(self.source), [])
        self.assertEqual(errors(self.page), [])
        self.assertEqual(PROOF.search(self.source).group(), PROOF.search(self.page).group())

    def test_primary_research_link_matches_existing_about_evidence(self):
        about = (ROOT / '_source/about.html').read_text(encoding='utf-8')
        self.assertIn('href="' + LINKS[0] + '"', about)
        self.assertIn('href="' + LINKS[1] + '"', self.page)
        self.assertIn('href="' + LINKS[2] + '"', self.page)
        self.assertIn('Journal of Accounting Research', self.page)
        self.assertNotIn('MIT Research Affiliate', PROOF.search(self.page).group())

    def test_change_is_only_one_publicly_reviewable_section(self):
        # This is an original-release diff assertion. Later homepage edits are
        # independently tested above, not removed by historical rewinding.
        for name in ('_source/home.html', 'index.html'):
            with self.subTest(file=name):
                old_hash, new_hash = history.records()['files'][name]
                current = reviewed_bytes(RELEASE, name, new_hash).decode('utf-8')
                before = reviewed_bytes(PARENT, name, old_hash)
                block = PROOF.search(current).group() + '\n'
                self.assertEqual(current.count(block), 1)
                self.assertEqual(current.replace(block, '', 1).encode('utf-8'), before)

    def test_local_build_live_inventory_and_canonical_are_unchanged(self):
        self.assertEqual(build.build_outputs()[Path('index.html')], self.page)
        self.assertEqual(check_live.targets()['/'], (200, self.page.encode('utf-8')))
        self.assertEqual(self.page.count('rel="canonical" href="https://nolankido.com/"'), 1)
        self.assertIn('AI Works, Human Decides', self.page)

    def test_native_layout_reuses_existing_responsive_cards(self):
        css = (ROOT / 'assets/site-core.css').read_text(encoding='utf-8')
        self.assertIn('.identity-readings { display: grid;', css)
        self.assertIn('grid-template-columns: minmax(0, 1fr);', css)
        self.assertIn('max-width: 900px', css)
        self.assertNotIn('<script', PROOF.search(self.page).group())

    def test_invalid_or_inflated_proof_examples_fail_closed(self):
        block = PROOF.search(self.page).group()
        for tampered in (
            self.page.replace(block, '', 1),
            self.page.replace(LINKS[0], '/not-a-real-research-source/', 1),
            self.page.replace('Gross cashes are not profit.', 'Tournament profit is proven.', 1),
            self.page.replace('class="identity-reading"', 'class="other-card"', 1),
            self.page.replace(block, block + '\n' + block, 1),
        ):
            with self.subTest(sample=tampered[:70]):
                self.assertTrue(errors(tampered))


class HomepageEvidenceHistoryTests(unittest.TestCase):
    def test_exact_complete_reviewed_revisions_and_parents(self):
        for name, (old, new) in history.records()['files'].items():
            with self.subTest(file=name):
                release = reviewed_bytes(RELEASE, name, new)
                before = reviewed_bytes(history.PARENT, name, old)
                self.assertEqual(history.before(name, release), before)

    def test_unknown_bytes_or_paths_never_rewind(self):
        for name in history.records()['files']:
            value = (ROOT / name).read_bytes()
            self.assertEqual(history.before(name, value + b'OTHER'), value + b'OTHER')
            self.assertEqual(history.before('different/' + name, value), value)

    def test_added_unit_tests_are_explicitly_pinned(self):
        for name, expected in history.records()['added'].items():
            release = reviewed_bytes(RELEASE, name, expected)
            self.assertTrue(history.is_added_file(name, release))
            self.assertFalse(history.is_added_file(name, release + b'OTHER'))


if __name__ == '__main__':
    unittest.main()
