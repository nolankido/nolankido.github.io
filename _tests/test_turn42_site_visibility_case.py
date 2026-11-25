"""The public AI-assisted website case has a dated, source-bounded release trail."""

import json
import re
from datetime import date
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build
import check_live
from reviewed_release import read as reviewed_bytes
import turn42_site_visibility_history as history

CASE_START = 'id="site-visibility-evidence"'
CASE_END = '</section>'
CASE_LINK = '/technology/ai-website-visibility/'
PR_NUMBERS = (170, 171, 172, 194, 195, 196, 197)
CHECKS = ("230 generated files", "26 of 26", "13,899 internal links", "206 HTML pages", "201 URLs")
RELEASE = "8a555c12ae7d38f77721b0344650bcefe6255736"


def case_section(text: str) -> str:
    parts = text.split(CASE_START, 1)
    return parts[1].split(CASE_END, 1)[0] if len(parts) == 2 else ""


def case_errors(text: str) -> list[str]:
    section = case_section(text)
    errors = []
    if not section:
        return ["public website-visibility case missing"]
    for number in PR_NUMBERS:
        url = f'https://github.com/nolankido/nolankido.github.io/pull/{number}'
        if section.count('href="' + url + '"') != 1:
            errors.append(f"public source PR {number} absent or duplicated")
    if section.count('href="' + CASE_LINK + '"'):
        errors.append("case incorrectly links to itself instead of its sources")
    for count in CHECKS:
        if count not in section:
            errors.append("missing bounded release check: " + count)
    for boundary in ("not a claimed client deployment", "did not infer current-cut titles",
                     "not a claim that AI output was independently reviewed", "Not established:",
                     "YouTube subscriptions"):
        if boundary not in section:
            errors.append("missing evidence or human-review boundary: " + boundary)
    for id_value in ("site-visibility-checks", "site-visibility-choices", "site-visibility-limits"):
        if section.count('id="' + id_value + '"') != 1:
            errors.append("missing or repeated case section: " + id_value)
    if 'href="/#home-proof-title"' not in section:
        errors.append("missing visible evidence shortcut route")
    if 'href="https://www.youtube.com/@NolanPoker"' not in section:
        errors.append("NolanPoker identity connection missing")
    if any(x in section for x in ("search rankings increased", "AI citations increased", "subscribed automatically", "<iframe")):
        errors.append("unsupported outcome or embedded channel claim")
    return errors


def revision_errors(route, source, effective, lastmods, schema):
    """Validate current revisions without resetting original publication dates."""
    errors = []
    floors = {'/about/': '2026-11-13', '/technology/': '2026-11-13',
              CASE_LINK: '2026-11-06'}
    try:
        dates = [date.fromisoformat(value) for value in (source, effective)]
        if [d.isoformat() for d in dates] != [source, effective]:
            raise ValueError('noncanonical calendar date')
    except (TypeError, ValueError):
        return ['invalid reviewed revision date']
    if dates[0] < date.fromisoformat(floors[route]) or dates[1] < dates[0]:
        errors.append('reviewed revision was backdated')
    if lastmods != [effective]:
        errors.append('sitemap revision must match the current effective manifest')
    if schema.get('url') != 'https://nolankido.com' + route:
        errors.append('structured canonical differs from reviewed route')
    if route == '/about/':
        if schema.get('@type') != 'ProfilePage' or 'dateModified' in schema:
            errors.append('ProfilePage must not invent a day-only modification timestamp')
    else:
        if schema.get('dateModified') != effective:
            errors.append('structured revision differs from current effective manifest')
        if route == CASE_LINK and (schema.get('@type') != 'Article'
                                  or schema.get('datePublished') != '2026-11-03'):
            errors.append('original Article publication identity must be preserved')
        elif route == '/technology/' and schema.get('@type') != 'CollectionPage':
            errors.append('Technology must retain its CollectionPage identity')
    return errors


class CurrentRevisionControls(unittest.TestCase):
    def test_actual_draft_revision_contract(self):
        for route, value, schema in (
            ('/about/', '2026-11-24', {'@type': 'ProfilePage'}),
            ('/technology/', '2026-11-20', {'@type': 'CollectionPage', 'dateModified': '2026-11-20'}),
            (CASE_LINK, '2026-11-21', {'@type': 'Article', 'datePublished': '2026-11-03', 'dateModified': '2026-11-21'}),
        ):
            with self.subTest(route=route):
                schema['url'] = 'https://nolankido.com' + route
                self.assertEqual(revision_errors(route, value, value, [value], schema), [])

    def test_later_reviewed_search_revision_and_sitemap_agree(self):
        schema = {'@type': 'CollectionPage', 'url': 'https://nolankido.com/technology/',
                  'dateModified': '2026-11-25'}
        self.assertEqual(revision_errors('/technology/', '2026-11-20', '2026-11-25', ['2026-11-25'], schema), [])

    def test_backdated_missing_duplicate_and_wrong_schema_dates_fail(self):
        route = '/technology/'
        value = '2026-11-20'
        schema = {'@type': 'CollectionPage', 'url': 'https://nolankido.com' + route, 'dateModified': value}
        for source, effective, lastmods, record in (
            ('2026-11-12', value, [value], schema),
            ('2026-11-24', value, [value], schema),
            ('2026-11-31', value, [value], schema),
            (value, value, [], schema),
            (value, value, [value, value], schema),
            (value, value, ['2026-11-13'], schema),
            (value, value, [value], {**schema, 'dateModified': '2026-11-13'}),
            (value, value, [value], {**schema, 'url': 'https://example.invalid/'}),
        ):
            with self.subTest(source=source, effective=effective, lastmods=lastmods, record=record):
                self.assertTrue(revision_errors(route, source, effective, lastmods, record))

    def test_profile_day_only_date_and_reset_article_publication_fail(self):
        value = '2026-11-24'
        profile = {'@type': 'ProfilePage', 'url': 'https://nolankido.com/about/', 'dateModified': value}
        self.assertTrue(revision_errors('/about/', value, value, [value], profile))
        article = {'@type': 'Article', 'url': 'https://nolankido.com' + CASE_LINK,
                   'dateModified': value, 'datePublished': value}
        self.assertTrue(revision_errors(CASE_LINK, value, value, [value], article))


class WebsiteVisibilityCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case_source = (ROOT / "_source/technology/ai-website-visibility.html").read_text(encoding="utf-8")
        cls.case_public = (ROOT / "technology/ai-website-visibility/index.html").read_text(encoding="utf-8")
        cls.about_source = (ROOT / "_source/about.html").read_text(encoding="utf-8")
        cls.about = (ROOT / "about/index.html").read_text(encoding="utf-8")

    def test_public_case_links_source_records_and_explicit_limits(self):
        for item in (self.case_source, self.case_public):
            with self.subTest(generated=(item is self.case_public)):
                self.assertEqual(case_errors(item), [])
                self.assertNotIn("\u2014", case_section(item))
        self.assertEqual(self.case_source.count(CASE_START), 1)
        self.assertEqual(self.case_public.count(CASE_START), 1)

    def test_about_evidence_route_finds_the_case_without_duplication(self):
        for item in (self.about_source, self.about):
            self.assertEqual(item.count('href="' + CASE_LINK + '"'), 1)
            self.assertIn("actual releases, checks and results that remain unmeasured", item)
            self.assertNotIn("\u2014", item)
        self.assertLess(self.about.find(CASE_LINK), self.about.find('id="public-work-elsewhere"'))

    def test_deterministic_generation_and_dated_sitemap(self):
        expected = build.build_outputs()
        for path in (Path("about/index.html"), Path("technology/index.html"), Path("technology/ai-website-visibility/index.html"), Path("sitemap.xml")):
            self.assertEqual(expected[path], (ROOT / path).read_text(encoding="utf-8"), path)
        manifest = {p["path"]: p for p in json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))}
        effective = {p["path"]: p for p in build.public_pages()}
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        for route in ("/about/", "/technology/", CASE_LINK):
            with self.subTest(route=route):
                rows = [node for node in sitemap if node.findtext("{*}loc") == "https://nolankido.com" + route]
                self.assertEqual(len(rows), 1)
                lastmods = [el.text for el in rows[0].findall("{*}lastmod")]
                html = (ROOT / route.strip("/") / "index.html").read_text(encoding="utf-8")
                records = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
                self.assertEqual(len(records), 1)
                schema = json.loads(records[0])
                self.assertEqual(revision_errors(route, manifest[route]["updated"],
                                                 effective[route]["updated"], lastmods, schema), [])
                if route == CASE_LINK:
                    self.assertEqual(manifest[route]["date"], "2026-11-03")
                    self.assertEqual(effective[route]["date"], "2026-11-03")
        targets = check_live.targets()
        for route, path in (("/about/", "about/index.html"), ("/technology/", "technology/index.html"), (CASE_LINK, "technology/ai-website-visibility/index.html")):
            self.assertEqual(targets[route], (200, (ROOT / path).read_bytes()))

    def test_broken_sources_and_inflated_claims_are_detected(self):
        cases = (
            self.case_source.replace("/pull/197", "/pull/999", 1),
            self.case_source.replace("26 of 26", "100 of 100", 1),
            self.case_source.replace("not a claimed client deployment", "a client success", 1),
            self.case_source.replace("Not established:", "Search rankings increased:", 1),
            self.case_source.replace('id="site-visibility-choices"', 'id="missing-gate"', 1),
        )
        for altered in cases:
            with self.subTest(change=altered[altered.find(CASE_START):][:65]):
                self.assertTrue(case_errors(altered))
        changed = self.about_source.replace('href="' + CASE_LINK + '"', 'href="/technology/#no-such-evidence"', 1)
        self.assertEqual(changed.count('href="' + CASE_LINK + '"'), 0)

    def test_exact_historical_bridge_does_not_hide_unreviewed_edits(self):
        self.assertEqual(len(history.records()["files"]), 7)
        for path, (prior_hash, current_hash) in history.records()["files"].items():
            with self.subTest(path=path):
                now = (ROOT / path).read_bytes()
                release = reviewed_bytes(RELEASE, path, current_hash)
                prior = reviewed_bytes(history.PARENT, path, prior_hash)
                self.assertEqual(history.before(path, release), prior)
                self.assertEqual(history.before(Path(path), release.decode("utf-8")), prior.decode("utf-8"))
                self.assertEqual(history.before(path, release + b"UNREVIEWED"), release + b"UNREVIEWED")
                self.assertEqual(history.before(path, now + b"UNREVIEWED"), now + b"UNREVIEWED")
                self.assertEqual(history.before("not-this-release/" + path, now), now)

    def test_pinned_release_loader_rejects_wrong_bytes_and_mutable_refs(self):
        path, (_, expected) = next(iter(history.records()["files"].items()))
        self.assertEqual(history.blob(reviewed_bytes(RELEASE, path, expected)), expected)
        with self.assertRaises(AssertionError):
            reviewed_bytes(RELEASE, path, "0" * 40)
        with self.assertRaises(ValueError):
            reviewed_bytes("main", path, expected)
        with self.assertRaises(ValueError):
            reviewed_bytes(RELEASE, "../" + path, expected)


if __name__ == "__main__":
    unittest.main()
