"""Turn 25: real AI-assisted public identity correction with reproducible limits."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build

SOURCE = ROOT / "_source/technology/home.html"
PUBLIC = ROOT / "technology/index.html"
CHECKER = ROOT / "downloads/identity-evidence-gate.py"
WORKBOOK = ROOT / "downloads/identity-evidence-case-workbook.md"
CASE_ID = "identity-claim-audit"
CASE_TITLE = "How an AI-assisted audit corrected a public identity claim."
BASE = "fa03f1b355d4b71291215168a7960fad97ec3ff0"


class CaseTags(HTMLParser):
    VOID = {"area", "br", "hr", "img", "input", "meta", "link", "source", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise AssertionError("Invalid case HTML: closing " + tag)


def case_section(text):
    marker = '<section class="section folio-row" id="' + CASE_ID + '"'
    assert text.count(marker) == 1
    begin = text.index(marker)
    return text[begin:text.index("</section>", begin) + len("</section>")]


class IdentityEvidenceCaseTests(unittest.TestCase):
    def test_same_public_case_in_source_and_generated_technology(self):
        source = SOURCE.read_text(encoding="utf-8")
        page = PUBLIC.read_text(encoding="utf-8")
        self.assertEqual(case_section(source), case_section(page))
        html = case_section(page)
        self.assertEqual(page.count('id="' + CASE_ID + '"'), 1)
        self.assertIn('id="identity-claim-audit-title"', html)
        self.assertIn('role="region"', html)
        self.assertIn('tabindex="0"', html)
        self.assertEqual(html.count('<th scope="row">'), 4)
        self.assertIn('/downloads/identity-evidence-gate.py', html)
        self.assertIn('/downloads/identity-evidence-case-workbook.md', html)
        self.assertIn('This does not establish', html.replace("It does not establish", "This does not establish"))
        self.assertNotIn("\u2014", html)
        parsed = CaseTags()
        parsed.feed(html)
        self.assertEqual(parsed.stack, [])

    def test_home_about_and_first_screen_link_to_exact_case(self):
        for path in ("_source/about.html", "about/index.html", "_source/home.html", "index.html"):
            body = (ROOT / path).read_text(encoding="utf-8")
            self.assertEqual(body.count('href="/technology/#identity-claim-audit"'), 1, path)
            self.assertNotIn("\\u0027", body)
        self.assertEqual((ROOT / "_source/about.html").read_text().count("How I handle credibility claims:"), 1)
        tech = SOURCE.read_text()
        self.assertIn('href="#identity-claim-audit">See an AI-assisted claim corrected.', tech)
        self.assertLess(tech.index('href="#identity-claim-audit"'), tech.index('id="' + CASE_ID + '"'))
        self.assertLess(tech.index('id="' + CASE_ID + '"'), tech.index('id="site-visibility-evidence"'))

    def test_case_is_covered_by_the_local_find_index(self):
        html = (ROOT / "find/index.html").read_text()
        match = re.search(r'<script type="application/json" id="find-section-data">(.*?)</script>', html)
        self.assertIsNotNone(match)
        index = json.loads(match.group(1))
        rows = index["pages"]["technology"][""]
        i = rows.index("identity-claim-audit-title")
        self.assertEqual(rows[i + 1], CASE_TITLE)
        self.assertEqual(rows[i + 2], "site-visibility-evidence-title")

    def test_original_source_and_generated_outputs_stay_aligned(self):
        outputs = build.build_outputs()
        for path in ("technology/index.html", "about/index.html", "index.html", "find/index.html"):
            with self.subTest(path=path):
                self.assertEqual(outputs[Path(path)], (ROOT / path).read_text(encoding="utf-8"))

    def test_case_has_checkable_public_provenance_and_boundaries(self):
        body = case_section(PUBLIC.read_text(encoding="utf-8"))
        sheet = WORKBOOK.read_text(encoding="utf-8")
        for item in (BASE, "a1e2f1c64e185c3d97fc813f47c75968cc769ab9",
                     "https://github.com/nolankido/nolankido.github.io/pull/180",
                     "10.1111/j.1475-679X.2012.00447.x"):
            self.assertIn(item, sheet)
        for phrase in ("not a current position", "human", "no network", "not a truth checker"):
            self.assertIn(phrase, body.lower())
        self.assertIn("search-traffic growth", sheet)
        self.assertNotIn("\u2014", sheet)

    def test_script_five_synthetic_self_checks(self):
        result = subprocess.run([sys.executable, str(CHECKER), "--self-test"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: 5/5 synthetic checks", result.stdout)

    def test_real_public_before_after_diff_and_tamper_detection(self):
        before = subprocess.check_output(
            ["git", "show", BASE + ":assets/nolan-kido-identity.jsonld"], cwd=ROOT
        ).decode("utf-8")
        after = (ROOT / "assets/nolan-kido-identity.jsonld").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as folder:
            old = Path(folder) / "before.jsonld"
            new = Path(folder) / "after.jsonld"
            old.write_text(before, encoding="utf-8")
            new.write_text(after, encoding="utf-8")
            command = [sys.executable, str(CHECKER), "--before", str(old),
                       "--after", str(new)]
            good = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            self.assertIn("PASS: scoped structural checks", good.stdout)
            changed = json.loads(after)
            person = next(n for n in changed["@graph"] if n["@type"] == "Person")
            person["affiliation"] = [{"roleName": "unverified"}]
            new.write_text(json.dumps(changed), encoding="utf-8")
            bad = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)
            self.assertIn("Sensitive field still published: affiliation", bad.stdout)
            new.write_text("{ broken", encoding="utf-8")
            invalid = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("INPUT ERROR", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
