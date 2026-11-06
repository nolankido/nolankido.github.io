"""Independent public AI reply audit, reproducible without GitHub Actions or model calls."""
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
import json
import re
import runpy
import shutil
import subprocess
import sys
import unittest
from test_site import ROOT, build, Page

import reply_audit_case
import build_reply_audit_case
import site_find
import player_find
import follow


class EvidenceText(HTMLParser):
    """Read visible example text without treating emphasis as a quotation edit."""
    IDS = {'reply-audit-source-review', 'reply-audit-archived-reply',
           'reply-audit-synthetic-refund', 'reply-audit-screen-result'}
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.records = {}
        self.active = None
        self.depth = 0
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if self.active is not None:
            if tag not in self.VOID:
                self.depth += 1
            if tag == 'p':
                self.active['paragraphs'] += 1
        elif values.get('id') in self.IDS:
            row = {'tag': tag, 'text': '', 'cite': values.get('cite'), 'paragraphs': 0}
            self.records.setdefault(values['id'], []).append(row)
            self.active = row
            self.depth = 1

    def handle_data(self, data):
        if self.active is not None:
            self.active['text'] += data

    def handle_endtag(self, tag):
        if self.active is not None and tag not in self.VOID:
            self.depth -= 1
            if self.depth == 0:
                self.active = None


class IndependentReplyAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.article = (ROOT / reply_audit_case.OUTPUT).read_text(encoding="utf-8")
        cls.source = (ROOT / reply_audit_case.SOURCE).read_text(encoding="utf-8")
        cls.audit = runpy.run_path(str(ROOT / reply_audit_case.TOOL))
        cls.complaint = next(case for case in cls.audit['EXAMPLES'] if case.case_id == 'cafe-complaint')

    def test_source_matches_compiler_and_public_identity(self):
        self.assertEqual(self.article, build_reply_audit_case.render())
        self.assertIn(self.source, self.article)
        record = reply_audit_case.record(ROOT)
        self.assertEqual(record["path"], reply_audit_case.ROUTE)
        self.assertEqual(record['date'], '2026-11-03')
        self.assertEqual(record['updated'], '2026-11-05')
        self.assertIn('Updated <time datetime="2026-11-05">November 5, 2026</time>', self.article)
        page = Page(self.article)
        self.assertEqual(len(page.tags("h1")), 1)
        self.assertEqual(len(page.tags("main")), 1)
        self.assertEqual([a.get("href") for a in page.tags("link")
                          if a.get("rel") == "canonical"], [reply_audit_case.URL])
        self.assertNotIn("—", self.article)
        self.assertNotIn("<iframe", self.article)
        self.assertNotIn("human approval performed", self.source.lower())

    def assert_faithful_visible_evidence(self, document):
        records = EvidenceText(document).records
        self.assertEqual(set(records), EvidenceText.IDS)
        self.assertTrue(all(len(rows) == 1 for rows in records.values()))
        quotes = {key: rows[0] for key, rows in records.items()}
        expected = {
            'reply-audit-source-review': self.complaint.fictional_review,
            'reply-audit-archived-reply': self.complaint.retained_output,
            'reply-audit-synthetic-refund': 'We have issued a refund to your card.',
        }
        for key, text in expected.items():
            self.assertEqual(quotes[key]['tag'], 'blockquote')
            self.assertEqual(quotes[key]['paragraphs'], 1)
            self.assertEqual(quotes[key]['text'].strip(), text, key)
        for key in ['reply-audit-source-review', 'reply-audit-archived-reply']:
            self.assertEqual(quotes[key]['cite'], self.audit['SOURCE'])
        self.assertIsNone(quotes['reply-audit-synthetic-refund']['cite'])
        result = quotes['reply-audit-screen-result']['text']
        self.assertEqual(re.findall(r'Offline screen:\s*([^\.]+)\.', result), ['no targeted flag'])
        self.assertEqual(re.findall(r'Human approval:\s*([^\.]+)\.', result), ['not performed'])
        return {key: quotes[key]['text'].strip() for key in expected}

    def test_visible_quotes_preserve_the_fixture_and_demonstrate_the_actual_screen(self):
        self.assert_faithful_visible_evidence(self.source)
        quotes = self.assert_faithful_visible_evidence(self.article)
        original = quotes['reply-audit-archived-reply']
        mutated = original + ' ' + quotes['reply-audit-synthetic-refund']
        for text, flagged, verdict in [(original, False, 'no_targeted_flag'),
                                       (mutated, True, 'flagged_for_review')]:
            result = self.audit['screen']('cafe-complaint', text)
            self.assertEqual(result['targeted_fact_omissions'], [])
            self.assertEqual(result['possible_unauthorized_financial_commitment'], flagged)
            self.assertEqual(result['screen'], verdict)
            self.assertEqual(result['human_approval'], 'not_performed')

    def test_evidence_checks_reject_changed_facts_misquotes_and_false_approval(self):
        mutations = [
            (self.complaint.fictional_review, self.complaint.fictional_review.replace('25', '20', 1)),
            ('our barista didn’t address your question promptly', 'our team answered your question promptly'),
            ('We have issued a refund to your card.', 'We have issued a refund.'),
            ('Offline screen: no targeted flag.', 'Offline screen: approved.'),
            ('Human approval: not performed.', 'Human approval: performed.'),
        ]
        for old, new in mutations:
            with self.subTest(mutation=new):
                changed = self.source.replace(old, new, 1)
                self.assertNotEqual(changed, self.source)
                with self.assertRaises(AssertionError):
                    self.assert_faithful_visible_evidence(changed)

    def test_public_examples_and_negative_controls_are_reproducible(self):
        result = subprocess.run([sys.executable, str(ROOT / reply_audit_case.TOOL),
                                 "--self-test"], cwd=ROOT, text=True,
                                capture_output=True, check=False, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["originals_screened"], 3)
        self.assertEqual(report["originals_with_targeted_flags"], 0)
        self.assertEqual(report["controls_intentionally_mutated"], 3)
        self.assertEqual(report["controls_flagged"], 3)
        self.assertFalse(report["human_approval_performed"])
        self.assertEqual(report["real_model_calls_this_run"], 0)
        self.assertEqual(report["network_requests_this_run"], 0)
        self.assertEqual({x["control"] for x in report["negative_controls"]},
                         {"remove_wait_duration", "remove_unanswered_question", "invent_refund"})

    def test_find_sitemap_feeds_have_one_canonical_article(self):
        outputs = build.build_outputs()
        self.assertEqual(outputs[Path("sitemap.xml")],
                         (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        for path in ("technology/index.html", "technology/local-ai-review-replies/index.html"):
            self.assertIn('href="' + reply_audit_case.ROUTE + '"',
                          (ROOT / path).read_text(encoding="utf-8"))
        items = player_find.add(ROOT, site_find.entries(ROOT, build.public_pages()))
        self.assertEqual([x["path"] for x in items].count(reply_audit_case.ROUTE), 1)
        self.assertIn('href="' + reply_audit_case.ROUTE + '"',
                      outputs[Path("find/index.html")])
        self.assertEqual(outputs[Path("find/index.html")],
                         (ROOT / "find/index.html").read_text(encoding="utf-8"))
        locations = [x.text for x in ET.fromstring(outputs[Path("sitemap.xml")]).iter()
                     if x.tag.endswith("}loc")]
        self.assertEqual(locations.count(reply_audit_case.URL), 1)
        namespace = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        sitemap = ET.fromstring(outputs[Path('sitemap.xml')])
        row = next(row for row in sitemap.findall('s:url', namespace)
                   if row.findtext('s:loc', namespaces=namespace) == reply_audit_case.URL)
        self.assertEqual(row.findtext('s:lastmod', namespaces=namespace), '2026-11-05')
        for name in ("technology/feed.xml", "writing.xml"):
            actual = (ROOT / name).read_text(encoding="utf-8")
            self.assertEqual(actual, outputs[Path(name)])
            items = ET.fromstring(actual).findall("./channel/item")
            entries = [x for x in items if x.findtext("link") == reply_audit_case.URL]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].findtext("guid"), reply_audit_case.URL)
            self.assertEqual(entries[0].findtext("pubDate"),
                             "Tue, 03 Nov 2026 00:00:00 GMT")
        combined = follow.combined(outputs, build.public_pages(), "https://nolankido.com", ROOT)
        self.assertEqual(combined, outputs[follow.OUTPUT])

    def test_publication_and_modification_dates_fail_closed_independently(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            for path in (reply_audit_case.SOURCE, reply_audit_case.OUTPUT,
                         reply_audit_case.TOOL, Path('technology/index.html')):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
            self.assertIsNotNone(reply_audit_case.record(root))
            html = root / reply_audit_case.OUTPUT
            current = html.read_text(encoding='utf-8')
            mutations = [
                ('property="article:published_time" content="2026-11-03"',
                 'property="article:published_time" content="2026-11-05"'),
                ('property="article:modified_time" content="2026-11-05"',
                 'property="article:modified_time" content="2026-11-03"'),
                ('"datePublished": "2026-11-03"', '"datePublished": "2026-11-05"'),
                ('"dateModified": "2026-11-05"', '"dateModified": "2026-11-03"'),
                ('Updated <time datetime="2026-11-05">', 'Updated <time datetime="2026-11-03">'),
                ('November 5, 2026</time>', 'November 3, 2026</time>'),
            ]
            for old, new in mutations:
                with self.subTest(mutation=new):
                    changed = current.replace(old, new, 1)
                    self.assertNotEqual(changed, current)
                    html.write_text(changed, encoding='utf-8')
                    with self.assertRaises(ValueError):
                        reply_audit_case.record(root)

    def test_broken_canonical_source_and_tool_fail_closed(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            for path in (reply_audit_case.SOURCE, reply_audit_case.OUTPUT,
                         reply_audit_case.TOOL, Path("technology/index.html")):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
            self.assertIsNotNone(reply_audit_case.record(root))
            html = root / reply_audit_case.OUTPUT
            current = html.read_text(encoding="utf-8")
            modified = current.replace('rel="canonical" href="' + reply_audit_case.URL + '"',
                                       'rel="canonical" href="https://invalid.example/"', 1)
            html.write_text(modified, encoding="utf-8")
            with self.assertRaises(ValueError):
                reply_audit_case.record(root)
            html.write_text(current.replace("<head>", '<head><meta name="robots" content="noindex">', 1),
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                reply_audit_case.record(root)
            html.write_text(current, encoding="utf-8")
            (root / reply_audit_case.TOOL).unlink()
            with self.assertRaises(ValueError):
                reply_audit_case.record(root)

    def test_offline_script_has_no_external_or_paid_transport(self):
        tool = (ROOT / reply_audit_case.TOOL).read_text(encoding="utf-8")
        for bad in ("import socket", "import urllib", "import requests",
                    "import subprocess", "OPENAI_API_KEY", "github.actions"):
            self.assertNotIn(bad, tool)
        self.assertIn("human_approval_performed", tool)
        self.assertIn("NEGATIVE CONTROLS", tool)


if __name__ == "__main__":
    unittest.main()
