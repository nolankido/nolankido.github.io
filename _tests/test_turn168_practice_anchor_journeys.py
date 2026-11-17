"""Turn 168: matched section navigation for the two mobile practice readers.

These tests verify that a reader can jump to a numbered review question, jump
to the corresponding check, and return to that same question without knowing
HTML or scanning a long page. No answer data is sent or stored.
"""
from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
QUESTION_HTML = ROOT / "downloads/poker-hand-review-practice-01.html"
KEY_HTML = ROOT / "downloads/poker-hand-review-practice-01-key.html"
QUESTION_MD = ROOT / "downloads/poker-hand-review-practice-01.md"
KEY_MD = ROOT / "downloads/poker-hand-review-practice-01-key.md"
BASE = "/downloads/poker-hand-review-practice-01.html"
CHECK = "/downloads/poker-hand-review-practice-01-key.html"

LABELS = (
    "1. Facts",
    "2. Pot math",
    "3. Options",
    "4. Reads",
    "5. Unknowns",
    "6. Result",
    "7. Next step",
)


def git_blob(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def issues(question: str, key: str, question_md: bytes, key_md: bytes) -> list[str]:
    errors: list[str] = []
    sources = ((question, question_md, "question"), (key, key_md, "check"))
    for html, source, prefix in sources:
        if html.count('data-source-blob="' + git_blob(source) + '"') != 1:
            errors.append(prefix + ": Markdown source fingerprint mismatch")
        if html.count("<script") or html.count("<form") or html.count("<iframe"):
            errors.append(prefix + ": unexpected script, form or external embed")
        if 'name="robots" content="noindex,follow"' not in html:
            errors.append(prefix + ": lost noindex duplicate protection")
        if 'href="#main"' not in html or 'id="main"' not in html:
            errors.append(prefix + ": missing keyboard skip target")
        css = re.search(r"<style>(.*?)</style>", html, re.S)
        if not css:
            errors.append(prefix + ": missing scoped inline CSS")
            continue
        for rule in (".step-nav{", ".step-nav a{", "min-height:44px",
                     ".practice-doc h2:target{", "outline:2px solid var(--red)",
                     "@media(max-width:480px)", ".step-nav,.compare-question{"):
            if rule not in css.group(1):
                errors.append(prefix + ": missing accessibility/print style " + rule)

        target_ids = re.findall(r'<h2 id="' + prefix + r'-([1-7])">', html)
        if target_ids != list("1234567"):
            errors.append(prefix + ": missing or unordered seven step targets")
        markdown_headings = re.findall(rb"(?m)^## ([1-7])\. ([^\r\n]+)", source)
        if [m[0].decode() for m in markdown_headings] != list("1234567"):
            errors.append(prefix + ": changed question/checking source order")
        for n, heading in markdown_headings:
            label = n.decode() + ". " + heading.decode("utf-8")
            if f'<h2 id="{prefix}-{n.decode()}">{label}</h2>' not in html:
                errors.append(prefix + ": numbered heading differs from Markdown")

        nav_label = ("Jump to a practice step" if prefix == "question"
                     else "Jump to a checking step")
        navs = re.findall(
            r'<nav class="step-nav" aria-label="' + re.escape(nav_label) +
            r'">(.*?)</nav>', html, re.S
        )
        if len(navs) != 1:
            errors.append(prefix + ": exactly one section nav required")
        else:
            links = re.findall(r'<a href="#([^"]+)">([^<]+)</a>', navs[0])
            expected = (
                [("case", "Scenario")] if prefix == "question" else []
            ) + [(prefix + "-" + str(i), LABELS[i - 1]) for i in range(1, 8)]
            if links != expected:
                errors.append(prefix + ": step links do not match the seven targets")
        if prefix == "question" and html.count('<h2 id="case">The entire fictional case</h2>') != 1:
            errors.append("question: missing original case heading")

    if question.count('href="' + CHECK + '"') != 1:
        errors.append("question: answer key must be linked exactly once")
    stop = question.find("<strong>Stop here.</strong>")
    first_key = question.find('href="' + CHECK + '"')
    if stop < 0 or first_key < stop:
        errors.append("question: key disclosed before all seven questions")
    for answer in ("**72,000**", "**20,000**", "**6,000**", "**26,000**",
                   "**14,000**", "**92,000**", "23.1%"):
        if answer in question:
            errors.append("question: arithmetic answer leaked")
    if key.count('class="compare-question"') != 7:
        errors.append("checking key: must link from all seven checks")
    pairs = re.findall(
        r'<h2 id="check-([1-7])">[^<]+</h2>\s*'
        r'<p class="compare-question"><a href="' +
        re.escape(BASE) + r'#question-([1-7])">Compare with question ([1-7])</a></p>',
        key
    )
    if pairs != [(str(n), str(n), str(n)) for n in range(1, 8)]:
        errors.append("checking key: compare links must match their question numbers")
    if '<a href="' + BASE + '">Return to questions</a>' not in key:
        errors.append("checking key: ordinary return link missing")
    if "class=\"audit-cards\"" not in key or key.count('class="audit-card"') != 14:
        errors.append("checking key: evidence and ledger cards must remain")
    if 'input type="checkbox"' not in key or key.count('input type="checkbox"') != 5:
        errors.append("checking key: five local self-checks must remain")
    for text in (question, key):
        if "\u2014" in text:
            errors.append("No em dash in authored static HTML")
    return errors


class PracticeAnchorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.question = QUESTION_HTML.read_text(encoding="utf-8")
        cls.key = KEY_HTML.read_text(encoding="utf-8")
        cls.question_md = QUESTION_MD.read_bytes()
        cls.key_md = KEY_MD.read_bytes()

    def test_step_nav_matches_original_questions_and_key(self):
        self.assertEqual(issues(
            self.question, self.key, self.question_md, self.key_md
        ), [])

    def test_answer_never_moves_before_stop_and_raw_files_stay_versioned(self):
        q = self.question
        k = self.key
        self.assertLess(q.index("<strong>Stop here.</strong>"),
                        q.index('href="' + CHECK + '"'))
        self.assertIn('data-source-blob="' + git_blob(self.question_md) + '"', q)
        self.assertIn('data-source-blob="' + git_blob(self.key_md) + '"', k)
        self.assertNotIn('href="' + CHECK + '"', q[:q.index("<strong>Stop here.</strong>")])
        for n in range(1, 8):
            self.assertIn('href="' + BASE + '#question-' + str(n) + '"', k)

    def test_negative_changes_are_rejected(self):
        changes = (
            (self.question.replace('id="question-5"', 'id="question-five"', 1), self.key),
            (self.question.replace('href="#question-5"', 'href="#question-4"', 1), self.key),
            (self.question.replace('<strong>Stop here.</strong>', '<strong>Continue.</strong>', 1), self.key),
            (self.question.replace('.practice-doc h2:target{', '.practice-doc h2:hover{', 1), self.key),
            (self.question, self.key.replace('#question-5">Compare with question 5',
                                             '#question-4">Compare with question 5', 1)),
            (self.question, self.key.replace('id="check-5"', 'id="check-five"', 1)),
            (self.question, self.key.replace('class="compare-question"', 'class="review-link"', 1)),
        )
        for index, (q, k) in enumerate(changes):
            with self.subTest(index=index):
                self.assertTrue(issues(q, k, self.question_md, self.key_md))


if __name__ == "__main__":
    unittest.main()
